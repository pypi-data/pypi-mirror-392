import json
from abc import ABC
from pathlib import Path

import requests
import time
from typing import Dict, Any, Union, BinaryIO, Optional, IO
from adxp_sdk.auth import BaseCredentials
from requests.exceptions import RequestException

from adxp_sdk.knowledges.enums import LoaderType, SplitterType
from adxp_sdk.knowledges.schemas import PolicyPayload, TagList, RetrievalOptions


class BaseHub(ABC):
    """
    공통 초기화 및 헤더 유틸을 제공하는 Base Hub.
    KnowledgeHub / ExternalKnowledgeHub 가 상속해서 사용.
    """

    def __init__(
            self,
            headers: Optional[Dict[str, str]] = None,
            base_url: Optional[str] = None,
            credentials: Optional[BaseCredentials] = None,
            timeout: float = 30.0,
    ):
        self.timeout = timeout

        if credentials is not None:
            self.credentials = credentials
            self.base_url = credentials.base_url.rstrip("/")
            self.headers: Optional[Dict[str, str]] = None
        elif headers is not None and base_url is not None:
            self.credentials = None
            self.base_url = base_url.rstrip("/")
            self.headers = headers
        else:
            raise ValueError(
                "Either credentials or (headers and base_url) must be provided"
            )

    def _headers(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Credentials.get_headers() 또는 self.headers 기반 기본 헤더에
        호출 시 전달한 extra 헤더를 병합해서 반환.

        - Authorization, Content-Type, Accept 등은 credentials.get_headers()나
          self.headers 쪽에서 구성한다고 가정.
        - 내부 dict를 오염시키지 않도록 반드시 copy해서 사용.
        """
        if self.credentials:
            base = dict(self.credentials.get_headers() or {})
        else:
            if self.headers is None:
                raise ValueError("Headers are not initialized.")
            base = dict(self.headers)

        if extra:
            base.update(extra)

        return base

    def _auth_only_headers(self) -> Dict[str, str]:
        """
        multipart/form-data 전송 시 사용.
        requests 가 Content-Type을 자동 설정하도록 두고,
        Authorization 만 꺼내 쓴다.
        """
        base = self._headers()
        auth: Dict[str, str] = {}
        if "Authorization" in base:
            auth["Authorization"] = base["Authorization"]
        return auth

    @staticmethod
    def _serialize_root_model_or_raw(value: Any) -> str:
        """
        RootModel (e.g. TagList, PolicyPayload) 이면 model_dump() 후 JSON 문자열로,
        이미 dict/list/etc 이면 그대로 JSON 문자열로 직렬화.
        """
        if hasattr(value, "model_dump"):
            payload = value.model_dump(mode="json", exclude_none=True)
        else:
            payload = value
        return json.dumps(payload, ensure_ascii=False)


class KnowledgeHub(BaseHub):
    """SDK for managing Knowledges"""

    def list_knowledge(
            self,
            page: int = 1,
            size: int = 10,
            is_active: bool | None = None,
            sort: str | None = None,
            _filter: str | None = None,
            search: str | None = None
    ) -> Dict[str, Any]:

        try:
            url = f"{self.base_url}/api/v1/knowledge/repos"
            params = {
                "is_active": is_active,
                "page": page,
                "size": size,
                "sort": sort,
                "filter": _filter,
                "search": search
            }

            resp = requests.get(url, headers=self._headers(), params=params)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to list knowledges: {str(e)}")

    def get_knowledge(
            self,
            repo_id: str,
    ) -> Dict[str, Any]:

        # UUID 객체가 넘어와도 문자열로 치환
        repo_id_str = str(repo_id)

        url = f"{self.base_url}/api/v1/knowledge/repos/{repo_id_str}"

        resp = requests.get(
            url,
            headers=self._headers(),
            timeout=self.timeout,
        )

        resp.raise_for_status()
        return resp.json()

    def create_knowledge(
            self,
            name: str,
            embedding_model_name: str,
            vector_db_id: str,
            loader: LoaderType,
            splitter: SplitterType,
            datasource_id: str | None = None,
            description: str | None = None,
            chunk_size: int | None = None,
            chunk_overlap: int | None = None,
            separator: str | None = None,
            custom_loader_id: str | None = None,
            custom_splitter_id: str | None = None,
            tool_id: str | None = None,
            processor_ids: list[str] | None = None,
    ) -> Dict[str, Any]:

        try:

            # 1. 기존 데이터소스 ID가 없으면 데이터소스 ID 생성
            if datasource_id is None:
                url = f"{self.base_url}/api/v1/datasources"
                datasource_name = f"datasource_{name}_{int(time.time())}"
                payload = {
                    "name": datasource_name
                }
                resp = requests.post(url, headers=self._headers(), json=payload)
                resp.raise_for_status()
                datasource_id = resp.json().get("id")

            # 2. Knowledge 리포지토리 생성
            url = f"{self.base_url}/api/v1/knowledge/repos"

            payload = {
                "name": name,
                "description": description,
                "datasource_id": datasource_id,
                "embedding_model_name": embedding_model_name,
                "loader": loader,
                "splitter": splitter,
                "vector_db_id": vector_db_id,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "separator": separator,
                "custom_loader_id": custom_loader_id,
                "custom_splitter_id": custom_splitter_id,
                "tool_id": tool_id,
                "processor_ids": processor_ids,

            }

            # 3. None 값인 항목 제거
            payload = {k: v for k, v in payload.items() if v is not None}

            resp = requests.post(url, headers=self._headers(), json=payload)
            resp.raise_for_status()

            return resp.json()

        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to create knowledge: {str(e)}")

    def update_knowledge(
            self,
            repo_id: str,
            name: str | None = None,
            description: str | None = None,
            loader: LoaderType | None = None,
            splitter: SplitterType | None = None,
            chunk_size: int | None = None,
            chunk_overlap: int | None = None,
            separator: str | None = None,
            custom_loader_id: str | None = None,
            custom_splitter_id: str | None = None,
            tool_id: str | None = None,
            processor_ids: list[str] | None = None,
    ) -> Dict[str, Any]:

        try:

            # 1. 기존 데이터 가져오기
            url = f"{self.base_url}/api/v1/knowledge/repos/{repo_id}"
            response = requests.get(url, headers=self._headers())
            response.raise_for_status()
            current_data = response.json()

            # 2. 파라미터 값이 있으면 파라미터 값, 없으면 기존 데이터 값으로 payload 생성
            url = f"{self.base_url}/api/v1/knowledge/repos/{repo_id}/edit"
            payload: Dict[str, Any] = {
                "name": name,
                "description": description,
                "loader": (
                    (loader.value if isinstance(loader, LoaderType) else loader)
                    or current_data.get("loader")
                ),
                "splitter": (
                    (splitter.value if isinstance(splitter, SplitterType) else splitter)
                    or current_data.get("splitter")
                ),
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "separator": separator,
                "custom_loader_id": custom_loader_id,
                "custom_splitter_id": custom_splitter_id,
                "tool_id": tool_id,
                "processor_ids": processor_ids,
            }

            resp = requests.put(url, json=payload, headers=self._headers())
            resp.raise_for_status()

            try:
                return resp.json()
            except requests.exceptions.JSONDecodeError:
                # 빈 응답 처리
                return {"message": "Successfully updated knowledge", "repo_id": repo_id}

        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to update knowledge: {str(e)}")

    def delete_knowledge(
            self,
            repo_id: str
    ) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}/api/v1/knowledge/repos/{repo_id}"

            resp = requests.delete(url, headers=self._headers())
            resp.raise_for_status()

            try:
                return resp.json()
            except requests.exceptions.JSONDecodeError:
                return {"repo_id": repo_id}

        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to delete knowledge: {str(e)}")

    def upload_knowledge_file(
            self,
            repo_id: str,
            datasource_id: str,
            file_path: str
    ) -> Dict[str, Any]:

        try:

            # 1. 파일 업로드
            upload_result = self.upload_file(
                file_path=file_path
            )

            # 2. 업로드 된 파일 ID 추출
            get_id_result = self.get_by_file_id(
                datasource_id=datasource_id,
                file_name=upload_result["data"][0]["file_name"],
            )

            # 3. 데이터소스 업데이트
            self.update_datasource(
                datasource_id=datasource_id,
                file_id=get_id_result["file_id"],
                file_name=upload_result["data"][0]["file_name"],
                temp_file_path=upload_result["data"][0]["temp_file_path"],
            )

            # 4. Knowledge 리포지토리 파일 List 업데이트
            self.update_knowledge_datasource(
                repo_id=repo_id
            )

            # 5. Knowledge 리포지토리 파일 인덱싱 실행
            indexing_result = self.indexing_knowledge(
                repo_id=repo_id,
                target_step="embedding_and_indexing"
            )

            repo_task_id = indexing_result.get("repo_task_id")

            return {
                "repo_id": repo_id,
                "datasource_id": datasource_id,
                "file_path": file_path,
                "repo_task_id": repo_task_id,
            }

        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to upload knowledge file: {str(e)}")

    def upload_file(self, file_path: str) -> Dict[str, Any]:

        try:
            # 1. 파일 업로드
            url = f"{self.base_url}/api/v1/datasources/upload/files"

            with open(file_path, 'rb') as file:
                files = {'files': file}

                headers = self._auth_only_headers()
                response = requests.post(url, files=files, headers=headers)

                response.raise_for_status()

            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                return {"message": "Successfully Upload File", "file_path": file_path}
        except Exception as e:
            raise Exception(f"Failed to Upload File: {e}")

    def get_by_file_id(self, datasource_id: str, file_name: str) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}/api/v1/datasources/{datasource_id}/files/queries/name"
            params = {
                "file_name": file_name
            }
            resp = requests.get(url, headers=self._headers(), params=params)
            resp.raise_for_status()
            try:
                return resp.json()
            except requests.exceptions.JSONDecodeError:
                return {"message": "Successfully retrieved file by Id", "datasource_id": datasource_id}
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to retrieve file by Id : {str(e)}")

    def update_datasource(
            self,
            datasource_id: str,
            file_id: str,
            file_name: str,
            temp_file_path: str
    ) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}/api/v1/datasources/{datasource_id}"

            payload = {
                "id": datasource_id,
                "type": "file",
                "modified_files": [
                    {
                        "file_id": file_id,
                        "file_name": file_name,
                        "temp_file_path": temp_file_path,
                        "status": "added"
                    }
                ]
            }

            resp = requests.put(url, headers=self._headers(), json=payload)
            resp.raise_for_status()
            try:
                return resp.json()
            except requests.exceptions.JSONDecodeError:
                return {"message": "Successfully updated datasource", "datasource_id": datasource_id}
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to update datasource: {str(e)}")

    def update_knowledge_datasource(self, repo_id: str) -> Dict[str, Any]:

        try:
            url = f"{self.base_url}/api/v1/knowledge/repos/{repo_id}"
            payload = {
                "update_mode": "append_modified_docs"
            }
            resp = requests.put(url, headers=self._headers(), json=payload)
            resp.raise_for_status()
            try:
                return resp.json()
            except requests.exceptions.JSONDecodeError:
                return {"message": "Successfully updated knowledge datasource", "repo_id": repo_id}
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to update knowledge datasource: {str(e)}")

    def indexing_knowledge(self, repo_id: str, target_step: str) -> Dict[str, Any]:

        try:
            url = f"{self.base_url}/api/v1/knowledge/repos/{repo_id}/indexing"

            payload = {
                "target_step": target_step
            }
            resp = requests.post(url, headers=self._headers(), json=payload)
            resp.raise_for_status()
            try:
                return resp.json()
            except requests.exceptions.JSONDecodeError:
                return {"message": "Successfully started indexing knowledge file", "repo_id": repo_id}
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to start indexing knowledge file: {str(e)}")


class ExternalKnowledgeHub(BaseHub):
    """SDK for managing External Knowledges"""

    def _get_retrieval_script_template(self) -> requests.Response:
        url = f"{self.base_url}/api/v1/knowledge/repos/external/template"

        try:
            resp = requests.get(
                url,
                headers=self._headers(),
                stream=True,
                timeout=self.timeout,
            )
        except requests.Timeout as e:
            raise RequestException(f"Timeout while downloading template: {e}") from e
        except requests.RequestException as e:
            raise RequestException(f"Network error while downloading template: {e}") from e

        if not (200 <= resp.status_code < 300):
            try:
                data = resp.json()
                msg = data.get("message") or data.get("detail") or str(data)
            except Exception:
                msg = resp.text[:500]
            raise RequestException(f"Failed to get retrieval script template.({resp.status_code}): {msg}")

        return resp

    def download_retrieval_script_template(
            self,
            dest: Union[str, Path, BinaryIO],
            *,
            chunk_size: int = 1024 * 64,
    ) -> None:
        """
        retrieval_script_template.py 를 dest 위치에 저장.

        Args:
            dest: 저장할 로컬 경로(str/Path) 또는 BinaryIO
            chunk_size: download 처리 시 chunk 크기
        """
        resp = self._get_retrieval_script_template()

        try:
            # 경로인 경우
            if isinstance(dest, (str, Path)):
                path = Path(dest)
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("wb") as f:
                    for chunk in resp.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                return

            # BinaryIO 인 경우
            if hasattr(dest, "write"):
                for chunk in resp.iter_content(chunk_size=chunk_size):
                    if chunk:
                        dest.write(chunk)
                return

            raise RequestException(f"Unsupported dest type: {type(dest)}")

        except OSError as e:
            raise RequestException(f"File write error: {e}") from e

    def create_external_knowledge(
            self,
            name: str,
            embedding_model_name: str,
            vector_db_id: str,
            index_name: str,
            script_file: Union[str, Path, IO[bytes]],
            description: Optional[str] = None,
            tags: Optional[TagList] = None,
            policy: Optional[PolicyPayload] = None,
            **extra_args: Any,
    ) -> Dict[str, Any]:
        """
        POST /api/v1/knowledge/repos/external

        multipart/form-data 필드:
          - name*                  (text)
          - description            (text)
          - embedding_model_name*  (text)
          - vector_db_id*          (text, UUID)
          - index_name*            (text)
          - script_file*           (file, binary)
          - tags                   (text, JSON)
          - policy                 (text, JSON)

        Returns:
          JSON dict (e.g. {"repo_id": "..."}).
        """
        url = f"{self.base_url}/api/v1/knowledge/repos/external"

        data: Dict[str, Any] = {
            "name": name,
            "embedding_model_name": embedding_model_name,
            "vector_db_id": str(vector_db_id),
            "index_name": index_name,
        }
        if description is not None:
            data["description"] = description

        if tags is not None:
            data["tags"] = self._serialize_root_model_or_raw(tags)

        if policy is not None:
            data["policy"] = self._serialize_root_model_or_raw(policy)

        # 이미 정의된 필드를 덮어쓰지 않는 선에서 extra_args 추가
        for key, value in extra_args.items():
            if key not in data:
                data[key] = value

        # script_file: path 또는 file-like 모두 지원
        def _open_file_if_needed(
                f: Union[str, Path, IO[bytes]]
        ) -> (IO[bytes], bool):
            if hasattr(f, "read"):
                return f, False  # 이미 열린 파일
            p = Path(f)
            return p.open("rb"), True

        file_obj, should_close = _open_file_if_needed(script_file)
        files = {
            # ("필드명": (파일명, 파일객체))
            "script_file": (
                getattr(file_obj, "name", "script.py"),
                file_obj,
            )
        }

        headers = self._auth_only_headers()

        try:
            resp = requests.post(
                url,
                data=data,
                files=files,
                headers=headers,
                timeout=self.timeout,
            )
        finally:
            if should_close:
                file_obj.close()

        resp.raise_for_status()
        return resp.json()

    def list_external_knowledges(
            self,
            page: int = 1,
            size: int = 10,
            is_active: Optional[bool] = None,
            sort: Optional[str] = None,
            _filter: Optional[str] = None,
            search: Optional[str] = None,
            **extra_params: Any,
    ) -> Dict[str, Any]:
        """
        GET /api/v1/knowledge/repos/external

        Project에 등록된 External Knowledge Repo 목록을 조회합니다.

        Query Parameters:
          - page       (int, optional, default: 1)
          - size       (int, optional, default: 10)
          - is_active  (bool, optional)
          - sort       (str, optional)
          - filter     (str, optional)
          - search     (str, optional)  # name, description 에 멀티 단어 포함 검색
          - extra_params (kwargs)       # 향후 추가 쿼리 파라미터 대응용

        Returns:
          - 서버에서 반환하는 JSON dict 그대로 (예: {"data": [...], "pagination": {...}})
        """
        url = f"{self.base_url}/api/v1/knowledge/repos/external"

        params: Dict[str, Any] = {
            "page": page,
            "size": size,
        }

        if is_active is not None:
            params["is_active"] = is_active
        if sort is not None:
            params["sort"] = sort
        if _filter is not None:
            params["filter"] = _filter
        if search is not None:
            params["search"] = search

        # 아직 SDK에 정의되지 않은 추가 쿼리 파라미터도 안전하게 전달
        for key, value in extra_params.items():
            if key not in params:
                params[key] = value

        resp = requests.get(
            url,
            params=params,
            headers=self._headers(),  # Authorization/Accept 포함
            timeout=self.timeout,
        )

        resp.raise_for_status()
        return resp.json()

    def get_external_knowledge(
            self,
            repo_id: str,
    ) -> Dict[str, Any]:
        """
        GET /api/v1/knowledge/repos/external/{repo_id}

        선택한 External Knowledge Repo 상세 정보를 조회합니다.

        Path Parameters:
          - repo_id (str | UUID): 조회할 External Repo ID

        Returns:
          - 서버에서 반환하는 JSON dict 그대로
            (예: {
                "name": "...",
                "description": "...",
                "embedding_model_id": "...",
                "vector_db_id": "...",
                "index_name": "...",
                "script": "...",
                "id": "...",
                "created_at": "...",
                "updated_at": "...",
                "is_active": true,
                "vector_db_type": "...",
                "vector_db_name": "...",
                "embedding_model_name": "...",
                "tags": [ ... ],
                ...
              })
        """
        # UUID 객체가 넘어와도 문자열로 치환
        repo_id_str = str(repo_id)

        url = f"{self.base_url}/api/v1/knowledge/repos/external/{repo_id_str}"

        resp = requests.get(
            url,
            headers=self._headers(),
            timeout=self.timeout,
        )

        resp.raise_for_status()
        return resp.json()

    def update_external_knowledge(
            self,
            repo_id: str,
            name: Optional[str] = None,
            description: Optional[str] = None,
            embedding_model_name: Optional[str] = None,
            index_name: Optional[str] = None,
            script_file: Optional[Union[str, Path, BinaryIO]] = None,
    ) -> Dict[str, Any]:
        """
        PUT /api/v1/knowledge/repos/external/{repo_id}

        Request body (multipart/form-data):
          - name                (optional, string)
          - description         (optional, string)
          - embedding_model_name(optional, string)
          - index_name          (optional, string)
          - script_file         (optional, file - retrieval script)
        """
        if (
                name is None
                and description is None
                and embedding_model_name is None
                and index_name is None
                and script_file is None
        ):
            raise ValueError("At least one field must be provided to update.")

        url = f"{self.base_url}/api/v1/knowledge/repos/external/{repo_id}"

        # text 필드만 모으기
        form_fields: Dict[str, Any] = {}
        if name is not None:
            form_fields["name"] = name
        if description is not None:
            form_fields["description"] = description
        if embedding_model_name is not None:
            form_fields["embedding_model_name"] = embedding_model_name
        if index_name is not None:
            form_fields["index_name"] = index_name

        # multipart/form-data 강제: text 필드도 files 형식으로 넣기
        files: Dict[str, Any] = {k: (None, v) for k, v in form_fields.items()}

        file_obj: Optional[BinaryIO] = None
        should_close = False

        if script_file is not None:
            # path / BinaryIO 모두 지원
            def _open_file_if_needed(
                    f: Union[str, Path, BinaryIO]
            ) -> tuple[BinaryIO, bool]:
                if hasattr(f, "read"):
                    return f, False
                p = Path(f)
                return p.open("rb"), True

            file_obj, should_close = _open_file_if_needed(script_file)
            files["script_file"] = (
                getattr(file_obj, "name", "retrieval_script.py"),
                file_obj,
            )

        headers = self._auth_only_headers()

        try:
            resp = requests.put(
                url,
                files=files,
                headers=headers,
                timeout=self.timeout,
            )
        finally:
            if should_close and file_obj is not None:
                file_obj.close()

        try:
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            # 응답 바디 일부를 함께 남겨 디버깅 용이하게
            body_preview = ""
            try:
                body_preview = resp.text[:500]
            except Exception:
                pass
            raise RequestException(
                f"Failed to update external repo: {e} {body_preview}"
            )

        return resp.json()

    def delete_external_knowledge(
            self,
            repo_id: str
    ) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}/api/v1/knowledge/repos/external/{repo_id}"

            resp = requests.delete(url, headers=self._headers())
            resp.raise_for_status()

            try:
                return resp.json()
            except requests.exceptions.JSONDecodeError:
                return {"repo_id": repo_id}

        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to delete knowledge: {str(e)}")

    def test_external_knowledge(
            self,
            embedding_model_name: str,
            vector_db_id: str,
            index_name: str,
            script_file: Union[str, Path, IO[bytes]],
            query: str,
            retrieval_options: Optional[RetrievalOptions] = None,
            **extra_args: Any,
    ) -> Dict[str, Any]:
        """
        POST /api/v1/knowledge/repos/external/test

        외부에서 생성된 Knowledge에 대한 설정이 올바른지 테스트하는 API.

        multipart/form-data 필드:
          - embedding_model_name*   (text)
          - vector_db_id*           (text, UUID)
          - index_name*             (text)
          - script_file*            (file, binary)
          - query*                  (text)
          - retrieval_options       (text, JSON)

        Returns:
          JSON dict (예: {"status": "success", "detail": [...]}).
        """
        url = f"{self.base_url}/api/v1/knowledge/repos/external/test"

        data: Dict[str, Any] = {
            "embedding_model_name": embedding_model_name,
            "vector_db_id": str(vector_db_id),
            "index_name": index_name,
            "query": query,
        }

        if retrieval_options is not None:
            data["retrieval_options"] = self._serialize_root_model_or_raw(
                retrieval_options
            )

        # 이미 정의된 키를 덮어쓰지 않는 선에서 extra_args 추가
        for key, value in extra_args.items():
            if key not in data:
                data[key] = value

        # script_file: path 또는 file-like 모두 지원
        def _open_file_if_needed(
                f: Union[str, Path, IO[bytes]]
        ) -> (IO[bytes], bool):
            if hasattr(f, "read"):
                return f, False  # 이미 열린 파일
            p = Path(f)
            return p.open("rb"), True

        file_obj, should_close = _open_file_if_needed(script_file)

        files = {
            "script_file": (
                getattr(file_obj, "name", "script.py"),
                file_obj,
            )
        }

        headers = self._auth_only_headers()

        try:
            resp = requests.post(
                url,
                data=data,
                files=files,
                headers=headers,
                timeout=self.timeout,
            )
        finally:
            if should_close:
                file_obj.close()

        try:
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            # 응답 일부 포함해서 디버깅 도움
            body_preview = ""
            try:
                body_preview = resp.text[:500]
            except Exception:
                pass
            raise RequestException(
                f"Failed to test external repo: {e} {body_preview}"
            )

        return resp.json()
