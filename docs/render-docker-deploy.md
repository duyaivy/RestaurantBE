# Deploy Docker từ GitHub Actions lên Render

GitHub Actions trên nhánh `release` build image `linux/amd64`, kiểm tra Django và Chroma qua hai container riêng, push lên `ghcr.io/duyaivy/restaurantbe`, rồi gọi Render deploy đúng digest. App secrets chỉ đặt ở Render; không đưa `.env` hoặc credentials vào Docker image hay build arguments.

Nếu đang có service native Python, xem [hướng dẫn chuyển service hiện tại sang image Docker](render-native-to-docker.md).

## Giữ Chroma local

Gắn Persistent Disk 1 GB tại `/var/data/chroma`, đặt `CHATBOT_CHROMA_DIR=/var/data/chroma`. `render.yaml` đã khai báo `runtime: image`, một instance và gói trả phí `0.5c-512mb`. Blueprint chỉ có hiệu lực khi bạn áp dụng trong Render; thay đổi file không tự sửa service đang chạy.

Disk chỉ có ở gói trả phí, chỉ một service instance truy cập được, không dùng trong build/pre-deploy. Deploy có gián đoạn ngắn. Docker image mới không làm mất dữ liệu trên disk. Docker volume local không tự trở thành disk trên Render.

Nếu tiếp tục dùng free, không có cách bảo đảm DB local tồn tại qua restart/deploy. Code hiện có thể ingest lại FAQ/catalog khi collection trống, nhưng đây là tái tạo index, tốn thời gian/API và không khôi phục dữ liệu chỉ tồn tại trong Chroma.

## Thiết lập lần đầu

1. Push thay đổi lên nhánh `release`. Trong GitHub Actions, chạy thủ công workflow **Build Docker and deploy Render**, chọn nhánh `release`, bỏ chọn `deploy`. Lần đầu push thiếu hook sẽ fail sớm; chạy thủ công build-only giải quyết vòng lặp chưa có image/service.
2. Sau khi image đã publish, trên Render tạo Web Service với **Existing Image**, URL `ghcr.io/duyaivy/restaurantbe:release`. Với package private, thêm registry credential GHCR bằng GitHub username + classic PAT có `read:packages` và quyền truy cập package (SSO nếu tổ chức yêu cầu). Không dùng `GITHUB_TOKEN` của workflow làm credential Render. Nếu dùng Blueprint, bật phần `image.creds` đang comment và dùng đúng tên credential.
3. Chọn paid compute, gắn disk `/var/data/chroma`, health check `/health/`. Không đặt native Python build/start command hoặc Docker command override; entrypoint thực hiện migrate, collectstatic và chạy Uvicorn. Cân nhắc RAM cao hơn nếu dùng embedding local; mặc định Blueprint dùng Jina API.
4. Export toàn bộ env của service native hiện tại và import vào service image. Giữ nguyên `SECRET_KEY`, URL PostgreSQL/Redis, payment secrets, provider/model/dimensions/collection. Dùng bảng dưới để override đường dẫn và server settings. `generateValue` của Blueprint phù hợp service mới; khi chuyển service cũ phải nhập lại SECRET_KEY cũ.
5. Copy deploy hook từ **service image** vào GitHub repository secret `RENDER_DEPLOY_HOOK_URL`. Hook của service native cũ sẽ không deploy prebuilt image đúng cách.
6. Chạy workflow với `deploy=true`, hoặc push lên `release`. Workflow gọi hook với `imgURL` URL-encoded chứa digest. Render yêu cầu registry/repository trùng với default image của service. Hook được chấp nhận chỉ chứng minh yêu cầu đã gửi; kiểm tra trạng thái deploy trong Dashboard và response `/health/` (`db` cũng phải là `ok`).
7. Xác minh endpoint API, Socket.IO, upload, thanh toán, chatbot trước khi chuyển frontend/domain sang service mới. Có thể đổi runtime/source qua Settings → Build → Source → Edit theo [tài liệu Render](https://render.com/docs/native-runtimes); xem hướng dẫn chuyển service được liên kết ở trên và kiểm tra disk/env sau đổi. Giữ service cũ cho tới khi service mới hoạt động.

Workflow chỉ publish/deploy nhánh `release`; manual trên nhánh khác bị skip. Deploy được serialize, không hủy build đang chạy. `GITHUB_TOKEN` tự có sẵn, cần workflow/package cho phép `packages: write`; không cần PAT push riêng. Giữ các image digest cũ trong GHCR để rollback.

## Biến môi trường runtime

Không copy giá trị mẫu local lên production. `render.yaml` có các khóa thông thường; các provider thay thế chỉ cần thêm trong Dashboard khi sử dụng. `sync: false` yêu cầu nhập giá trị khi tạo Blueprint, không đọc `.env` của máy bạn. Khi đang dùng Groq, có thể bỏ khai báo Gemini khỏi Blueprint nếu không dùng; tương tự tính năng Translation có thể tắt và bỏ các secret liên quan.

| Nhóm | Biến | Cấu hình |
| --- | --- | --- |
| Django | `DJANGO_SETTINGS_MODULE`, `ENV`, `SECRET_KEY` | `restaurantBE.settings.production`, `prod`, secret hiện tại |
| Server | `PORT`, `WEB_CONCURRENCY`, `LOG_LEVEL` | Render: `10000`, `1`, `info` (entrypoint cũng nhận `INFO`) |
| Logging/cache | `DJANGO_DB_LOG_LEVEL`, `DJANGO_CACHE_TIMEOUT_DEFAULT` | `WARNING`, `3600`; DB log level hiện chỉ được settings local sử dụng |
| URL/CORS | `ALLOWED_HOSTS`, `HOST`, `CLIENT_URL`, `CORS_ALLOWED_ORIGINS` | Domain BE + FE thực; HOST nên có `/` cuối; CORS phân cách bằng dấu phẩy |
| PostgreSQL | `DATABASE_URL` | Giữ URL hiện tại, bao gồm query `sslmode` nếu cần |
| PostgreSQL thay thế | `DB_NAME`, `DB_USERNAME`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Chỉ dùng khi không có DATABASE_URL; port thường `5432`; không đặt host `db` local trên Render |
| Redis | `REDIS_URL` | URL Redis hiện tại; không dùng hostname `redis` local trên Render |
| Media | `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` | Giữ thông tin upload hiện tại |
| VNPay | `VNPAY_TMN_CODE`, `VNPAY_HASH_SECRET`, `VNPAY_PAYMENT_URL`, `VNPAY_RETURN_URL`, `VNPAY_ORDER_TYPE` | Giữ môi trường thanh toán hiện tại; return URL phải trỏ BE thật |
| Chroma | `CHATBOT_CHROMA_DIR`, `CHATBOT_CHROMA_COLLECTION` | `/var/data/chroma`, collection hiện tại |
| Embedding | `CHATBOT_EMBEDDING_PROVIDER`, `CHATBOT_EMBEDDING_MODEL`, `CHATBOT_EMBEDDING_DIMENSIONS` | Giữ cấu hình index cũ; Blueprint: `jina`, `jina-embeddings-v3`, `1024` |
| Embedding options | `CHATBOT_EMBEDDING_DEVICE`, `CHATBOT_EMBEDDING_BATCH_SIZE`, `CHATBOT_EMBEDDING_NORMALIZE`, `CHATBOT_EMBEDDING_TIMEOUT_SECONDS`, `CHATBOT_EMBEDDING_BASE_URL` | `cpu`, `32`, `true`, `15`; base URL chỉ khi provider cần |
| Embedding secret | `CHATBOT_EMBEDDING_API_KEY` | API key của provider đã chọn |
| Embedding fallback | `EMBEDDING_API_KEY`, `JINA_API_KEY`, `NVIDIA_API_KEY` | Chỉ đặt khi sử dụng provider tương ứng; không cần đủ mọi key |
| LLM | `CHATBOT_LLM_PROVIDER`, `CHATBOT_LLM_MODEL`, `CHATBOT_LLM_TEMPERATURE`, `CHATBOT_LLM_MAX_TOKENS`, `CHATBOT_LLM_REASONING_ENABLED`, `CHATBOT_LLM_BASE_URL` | Giữ provider/model hiện tại; default Blueprint: Groq, 0.2, 800, false; base URL optional |
| LLM secret | `GROQ_API_KEY`, `GEMINI_API_KEY`, `OPENROUTER_API_KEY` | Chỉ cần key của provider sử dụng; embedding Gemini cũng có thể cần GEMINI_API_KEY |
| Translation | `GOOGLE_TRANSLATION_ENABLED`, `GOOGLE_TRANSLATION_PROJECT_ID`, `GOOGLE_TRANSLATION_LOCATION` | Nếu bật: project hiện tại, `global`; nếu không dùng đặt `false` |
| Google credentials | `GOOGLE_CREDENTIALS_JSON_BASE64` hoặc `GOOGLE_APPLICATION_CREDENTIALS` | Base64 JSON được giải mã runtime tại `/tmp/gcp-sa.json`; hoặc upload Render Secret File rồi trỏ `/etc/secrets/<file>`. Không dùng path máy local |

`PYTHON_VERSION` của native runtime không quyết định phiên bản image; Dockerfile dùng Python 3.11. `.env.example` dành cho local có embedding e5-small/384, khác default Jina/1024 của Render: không đổi kích thước collection cũ chỉ vì đổi deployment.

## Chuyển dữ liệu Chroma cũ và backup

Mount disk mới không tự sao chép DB cũ. Trước khi restart/redeploy service native đang có dữ liệu, ngừng ghi/ingest và tạo bản sao nhất quán của **toàn bộ thư mục** đang được `CHATBOT_CHROMA_DIR` sử dụng (hoặc mặc định `restaurantBE/chatbot/rag/.chroma`). Chỉ copy `chroma.sqlite3` là chưa đủ: index còn nằm trong các thư mục khác.

Chuyển bản sao qua kênh riêng, restore vào `/var/data/chroma` của service mới lúc ứng dụng không ghi. Disk không chia sẻ giữa hai service, vì vậy không thể chỉ gắn tên disk cũ vào service mới. Không commit DB hoặc đóng gói dữ liệu production vào image. Nếu dữ liệu gốc chỉ là FAQ/catalog có thể cho ingest lại vào disk rỗng; dữ liệu bổ sung phải chuyển hoặc khôi phục riêng.

Giữ provider/model/dimensions và collection khi dùng index cũ. Khi đổi embedding, tạo collection mới và re-ingest từ dữ liệu gốc. Sau chuyển, thử chatbot rồi redeploy lần nữa để xác nhận số document/dữ liệu còn nguyên. Snapshot disk của Render và bản sao nhất quán ngoài service giúp phục hồi; disk là persistence, không thay thế backup.

Local Compose vẫn dùng volume `chroma_data`, nhưng mount path đã đổi sang `/var/data/chroma`; volume cũ vẫn giữ dữ liệu ở root. Compose nhận env `.env` cho PostgreSQL/Redis bên ngoài, không tạo thêm hai service này. Cổng bên trong luôn `8000`, `PORT` local chỉ chọn cổng host. Container mới bắt đầu với một worker để hạn chế nhiều process tự bootstrap index cùng lúc.

## Kiểm tra

CI chạy shell syntax, lint test, build, `manage.py check`, `collectstatic`, import embedding CPU, ghi bằng VectorDBService trong container thứ nhất rồi đọc/query trong container mới dùng cùng volume; không gọi embedding API. Kiểm tra này xác nhận persistence khi thay container, không xác nhận disk/account/credentials thật trên Render. Migrate chỉ chạy lúc khởi động trên PostgreSQL thật, vì CI không nhận secrets production.

Docker cài PyTorch từ CPU wheel index để tránh kéo CUDA lên Render. Requirements giới hạn Transformers/Sentence Transformers để tương thích tokenizers của Chroma 0.5, và PostHog dưới 6 để giữ API telemetry mà Chroma 0.5 đang gọi. Việc này không đổi provider/model/dimensions runtime của bạn.

Nguồn: [Render persistent disks](https://render.com/docs/disks), [prebuilt images & deploy hook](https://render.com/docs/deploying-an-image), [Blueprint reference](https://render.com/docs/blueprint-spec), [GitHub publishing Docker images](https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images).

## Groq trả 404 khi chat

Nếu health/login hoạt động nhưng Groq trả 404, kiểm tra `CHATBOT_LLM_MODEL`. Lỗi `model_not_found` có thể là model không tồn tại hoặc API key/tài khoản không có quyền truy cập. Model có trên tài liệu công khai chưa chắc tài khoản của bạn gọi được. Ngày 14/10/2026, kiểm tra API key local của repo cho thấy `llama-3.1-8b-instant` không truy cập được; `openai/gpt-oss-20b` trả 200 và hỗ trợ JSON với `answer`/`suggest_items`. Cấu hình mẫu đã cập nhật sang model đã kiểm tra.

```dotenv
CHATBOT_LLM_PROVIDER=groq
CHATBOT_LLM_MODEL=openai/gpt-oss-20b
```

Local: sửa `.env`, rồi chạy `docker compose up -d --force-recreate web` để nạp env mới; chỉ restart container cũ không cập nhật env Docker. Render: sửa Environment tương ứng rồi redeploy. Thay đổi `render.yaml` không tự thay env của service tạo thủ công. Không cần đổi model embedding Jina hoặc reset Chroma khi chỉ đổi model tạo câu trả lời.

Backend Groq hiện dừng ngay với lỗi HTTP không thể khắc phục bằng retry (như 401/403/404/422) và trả thông tin model/error code; chỉ retry 429, 500/502/503/504 và lỗi kết nối/timeout. CI có regression test dùng API mock, không tiêu tốn quota.

Nguồn: [Groq model API](https://console.groq.com/docs/models), [Groq error codes](https://console.groq.com/docs/errors).
