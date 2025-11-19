from pixelarraycloudstorage.client import AsyncClient
from typing import Dict, Any, Optional, List, Tuple, AsyncGenerator
import os
import aiohttp
import mimetypes
import math
import time


class FileStorageManagerAsync(AsyncClient):
    async def upload(
        self, file_path: str, parent_id: Optional[int] = None
    ) -> Tuple[Dict[str, Any], bool]:
        """
        description:
            上传文件（合并了初始化、分片上传、完成上传三个步骤）
        parameters:
            file_path: 文件路径（str）
            parent_id: 父文件夹ID（可选）
        return:
            - data: 结果数据
            - success: 是否成功
        """
        final_result: Dict[str, Any] = {}
        final_success = False
        async for progress in self.upload_stream(file_path, parent_id):
            event = progress.get("event")
            if event == "error":
                return {}, False
            if event == "complete" and progress.get("success"):
                final_result = progress.get("result", {})
                final_success = True
        return final_result, final_success

    async def upload_stream(
        self, file_path: str, parent_id: Optional[int] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        description:
            上传文件（流式，返回生成器，包含进度信息）
        """
        chunk_size = 2 * 1024 * 1024  # 2MB
        upload_start = time.perf_counter()
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        total_size = len(file_bytes)
        file_name = os.path.basename(file_path)
        mime_type = mimetypes.guess_type(file_path)[0]
        init_data = {
            "filename": file_name,
            "file_type": mime_type,
            "total_size": total_size,
        }
        if parent_id is not None:
            init_data["parent_id"] = parent_id

        init_result, success = await self._request(
            "POST", "/api/file_storage/upload/init", json=init_data
        )
        if not success:
            yield {
                "event": "error",
                "percentage": 0,
                "total_chunks": 0,
                "remaining_chunks": 0,
                "total_bytes": total_size,
                "processed_bytes": 0,
                "speed": 0,
                "message": "初始化上传失败",
                "success": False,
            }
            return

        upload_id = init_result.get("upload_id")
        chunk_urls = init_result.get("chunk_urls", [])
        total_chunks = len(chunk_urls)

        if not upload_id or not chunk_urls:
            yield {
                "event": "error",
                "percentage": 0,
                "total_chunks": 0,
                "remaining_chunks": 0,
                "total_bytes": total_size,
                "processed_bytes": 0,
                "speed": 0,
                "message": "缺少上传ID或分片信息",
                "success": False,
            }
            return

        yield {
            "event": "init",
            "percentage": 0,
            "total_chunks": total_chunks,
            "remaining_chunks": total_chunks,
            "total_bytes": total_size,
            "processed_bytes": 0,
            "speed": 0,
            "message": "初始化完成，开始上传分片",
            "success": True,
        }

        parts: List[Dict[str, Any]] = []
        uploaded_bytes = 0

        async with aiohttp.ClientSession() as session:
            for idx, chunk_info in enumerate(chunk_urls):
                part_number = chunk_info.get("part_number")
                url = chunk_info.get("url")
                start = idx * chunk_size
                end = min(start + chunk_size, total_size)
                chunk_data = file_bytes[start:end]

                if not url or not part_number:
                    percentage = (
                        0
                        if total_size == 0
                        else min((uploaded_bytes / total_size) * 100, 100)
                    )
                    yield {
                        "event": "error",
                        "percentage": percentage,
                        "total_chunks": total_chunks,
                        "remaining_chunks": total_chunks - idx,
                        "total_bytes": total_size,
                        "processed_bytes": uploaded_bytes,
                        "speed": 0,
                        "message": "分片信息缺失",
                        "success": False,
                    }
                    return

                chunk_start = time.perf_counter()
                try:
                    async with session.put(url, data=chunk_data) as resp:
                        if resp.status != 200:
                            raise RuntimeError(
                                f"分片上传失败，状态码：{resp.status}"
                            )
                        etag = resp.headers.get("ETag", "").strip('"')
                        parts.append(
                            {
                                "part_number": part_number,
                                "etag": etag,
                            }
                        )
                except Exception as exc:
                    percentage = (
                        0
                        if total_size == 0
                        else min((uploaded_bytes / total_size) * 100, 100)
                    )
                    yield {
                        "event": "error",
                        "percentage": percentage,
                        "total_chunks": total_chunks,
                        "remaining_chunks": max(total_chunks - idx, 0),
                        "total_bytes": total_size,
                        "processed_bytes": uploaded_bytes,
                        "speed": 0,
                        "message": f"分片上传异常：{exc}",
                        "success": False,
                    }
                    return

                uploaded_bytes += len(chunk_data)
                duration = max(time.perf_counter() - chunk_start, 1e-6)
                speed = len(chunk_data) / duration
                percentage = (
                    100
                    if total_size == 0
                    else min((uploaded_bytes / total_size) * 100, 100)
                )

                yield {
                    "event": "chunk",
                    "percentage": percentage,
                    "total_chunks": total_chunks,
                    "remaining_chunks": max(total_chunks - (idx + 1), 0),
                    "total_bytes": total_size,
                    "processed_bytes": uploaded_bytes,
                    "chunk_index": idx,
                    "chunk_size": len(chunk_data),
                    "speed": speed,
                    "message": f"分片{idx + 1}/{total_chunks}上传完成",
                    "success": True,
                }

        complete_data = {
            "upload_id": upload_id,
            "parts": parts,
        }
        complete_result, success = await self._request(
            "POST", "/api/file_storage/upload/complete", json=complete_data
        )
        if not success:
            yield {
                "event": "error",
                "percentage": 100,
                "total_chunks": total_chunks,
                "remaining_chunks": 0,
                "total_bytes": total_size,
                "processed_bytes": total_size,
                "speed": 0,
                "message": "完成上传失败",
                "success": False,
            }
            return

        total_duration = max(time.perf_counter() - upload_start, 1e-6)
        yield {
            "event": "complete",
            "percentage": 100,
            "total_chunks": total_chunks,
            "remaining_chunks": 0,
            "total_bytes": total_size,
            "processed_bytes": total_size,
            "speed": total_size / total_duration if total_duration else 0,
            "message": "上传完成",
            "success": True,
            "result": complete_result,
        }

    async def list_files(
        self,
        parent_id: Optional[int] = None,
        is_folder: Optional[bool] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[Dict[str, Any]], bool]:
        """
        description:
            获取文件列表
        parameters:
            parent_id: 父文件夹ID（可选）
            is_folder: 是否只查询文件夹（可选）
            page: 页码（可选）
            page_size: 每页数量（可选）
        return:
            - data: 文件列表数据
            - success: 是否成功
        """
        data = {
            "page": page,
            "page_size": page_size,
        }
        if parent_id is not None:
            data["parent_id"] = parent_id
        if is_folder is not None:
            data["is_folder"] = is_folder

        result, success = await self._request(
            "POST", "/api/file_storage/files/list", json=data
        )
        if not success:
            return {}, False
        return result, True

    async def create_folder(
        self,
        folder_name: str,
        parent_id: Optional[int] = None,
    ) -> Tuple[Dict[str, Any], bool]:
        """
        description:
            创建文件夹
        parameters:
            folder_name: 文件夹名称
            parent_id: 父文件夹ID（可选）
        return:
            - data: 文件夹数据
            - success: 是否成功
        """
        data = {
            "folder_name": folder_name,
        }
        if parent_id is not None:
            data["parent_id"] = parent_id

        data, success = await self._request(
            "POST", "/api/file_storage/files/folder/create", json=data
        )
        if not success:
            return {}, False
        return data, True

    async def delete_file(
        self,
        record_id: int,
    ) -> Tuple[Dict[str, Any], bool]:
        """
        description:
            删除文件或文件夹
        parameters:
            record_id: 文件或文件夹ID
        return:
            - data: 结果数据
            - success: 是否成功
        """
        data, success = await self._request(
            "DELETE", f"/api/file_storage/files/{record_id}"
        )
        if not success:
            return {}, False
        return data, True

    async def get_folder_path(
        self,
        record_id: int,
    ) -> Tuple[List[Dict[str, Any]], bool]:
        """
        description:
            获取文件夹的完整路径
        parameters:
            record_id: 文件夹ID
        return:
            - data: 文件夹路径列表
            - success: 是否成功
        """
        data, success = await self._request(
            "GET", f"/api/file_storage/files/{record_id}/path"
        )
        if not success:
            return [], False
        # 如果data是字典，尝试获取data字段（因为API返回的是{"data": [...]}）
        if isinstance(data, dict):
            path_list = data.get("data", [])
            if isinstance(path_list, list):
                return path_list, True
        # 如果data本身就是列表，直接返回
        if isinstance(data, list):
            return data, True
        return [], False

    async def generate_signed_url(
        self,
        record_id: int,
        expires: int = 3600,
    ) -> Tuple[Dict[str, Any], bool]:
        """
        生成签名URL（异步版本）
        """
        data = {
            "expires": expires,
        }
        data, success = await self._request(
            "POST", f"/api/file_storage/files/{record_id}/generate_url", json=data
        )
        if not success:
            return {}, False
        return data, True

    async def download(
        self,
        record_id: int,
        save_path: str,
    ) -> Tuple[Dict[str, Any], bool]:
        """
        description:
            下载文件
        parameters:
            record_id: 文件记录ID
            save_path: 保存路径
        return:
            - data: 下载结果数据
            - success: 是否成功
        """
        final_result: Dict[str, Any] = {}
        final_success = False
        async for progress in self.download_stream(record_id, save_path):
            event = progress.get("event")
            if event == "error":
                return {}, False
            if event == "complete" and progress.get("success"):
                final_result = progress.get("result", {})
                final_success = True
        return final_result, final_success

    async def download_stream(
        self,
        record_id: int,
        save_path: str,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        description:
            下载文件（流式，返回生成器）
        """
        chunk_size = 2 * 1024 * 1024
        signed_url_data, success = await self.generate_signed_url(record_id)
        if not success:
            yield {
                "event": "error",
                "percentage": 0,
                "total_chunks": 0,
                "remaining_chunks": 0,
                "total_bytes": 0,
                "processed_bytes": 0,
                "speed": 0,
                "message": "生成签名URL失败",
                "success": False,
            }
            return

        signed_url = signed_url_data.get("signed_url")
        file_record = signed_url_data.get("file_record", {}) or {}
        total_size = file_record.get("file_size", 0) or 0

        if not signed_url:
            yield {
                "event": "error",
                "percentage": 0,
                "total_chunks": 0,
                "remaining_chunks": 0,
                "total_bytes": total_size,
                "processed_bytes": 0,
                "speed": 0,
                "message": "签名URL为空",
                "success": False,
            }
            return

        total_chunks = math.ceil(total_size / chunk_size) if total_size else 0

        yield {
            "event": "init",
            "percentage": 0,
            "total_chunks": total_chunks,
            "remaining_chunks": total_chunks,
            "total_bytes": total_size,
            "processed_bytes": 0,
            "speed": 0,
            "message": "开始下载文件",
            "success": True,
        }

        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)

        downloaded_bytes = 0
        chunk_index = 0
        download_start = time.perf_counter()

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(signed_url) as resp:
                    if resp.status != 200:
                        raise RuntimeError(f"文件下载失败，状态码：{resp.status}")

                    header_size = resp.headers.get("Content-Length")
                    if total_size == 0 and header_size:
                        try:
                            total_size = int(header_size)
                            total_chunks = (
                                math.ceil(total_size / chunk_size)
                                if total_size
                                else 0
                            )
                        except ValueError:
                            total_size = 0

                    with open(save_path, "wb") as f:
                        async for chunk in resp.content.iter_chunked(chunk_size):
                            chunk_start = time.perf_counter()
                            chunk_index += 1
                            downloaded_bytes += len(chunk)
                            f.write(chunk)

                            chunk_duration = max(
                                time.perf_counter() - chunk_start, 1e-6
                            )
                            instant_speed = len(chunk) / chunk_duration
                            percentage = (
                                0
                                if total_size == 0
                                else min(
                                    (downloaded_bytes / total_size) * 100, 100
                                )
                            )
                            remaining = (
                                max(total_chunks - chunk_index, 0)
                                if total_chunks
                                else 0
                            )

                            yield {
                                "event": "chunk",
                                "percentage": percentage,
                                "total_chunks": total_chunks,
                                "remaining_chunks": remaining,
                                "total_bytes": total_size,
                                "processed_bytes": downloaded_bytes,
                                "chunk_index": chunk_index - 1,
                                "chunk_size": len(chunk),
                                "speed": instant_speed,
                                "message": f"分片{chunk_index}/{total_chunks or '?'}下载完成",
                                "success": True,
                            }
            except Exception as exc:
                yield {
                    "event": "error",
                    "percentage": 0,
                    "total_chunks": total_chunks,
                    "remaining_chunks": total_chunks,
                    "total_bytes": total_size,
                    "processed_bytes": downloaded_bytes,
                    "speed": 0,
                    "message": f"下载过程中发生错误：{exc}",
                    "success": False,
                }
                return

        total_duration = max(time.perf_counter() - download_start, 1e-6)
        result = {
            "total_size": total_size,
            "success": True,
        }
        yield {
            "event": "complete",
            "percentage": 100,
            "total_chunks": total_chunks,
            "remaining_chunks": 0,
            "total_bytes": total_size,
            "processed_bytes": total_size if total_size else downloaded_bytes,
            "speed": (total_size or downloaded_bytes)
            / max(total_duration, 1e-6),
            "message": "下载完成",
            "success": True,
            "result": result,
        }
