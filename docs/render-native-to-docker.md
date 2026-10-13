# Chuyển service Render đang chạy Python sang Docker image từ GitHub

Mục tiêu: GitHub Actions build/test/push image; Render pull và chạy image đó. PostgreSQL và Redis cloud hiện tại tiếp tục được dùng. Không tạo thêm DB hoặc Redis.

## Env nằm ở đâu?

| Nơi đặt | Nội dung |
| --- | --- |
| Render → service → Environment | Toàn bộ env BE: DATABASE_URL, REDIS_URL, SECRET_KEY, Cloudinary, VNPay, API key chatbot, Google credentials, URL/CORS và các cấu hình khác |
| GitHub → repository → Settings → Secrets and variables → Actions | Một repository secret tên `RENDER_DEPLOY_HOOK_URL`, lấy từ service Render chạy image |
| GitHub tự cấp cho workflow | `GITHUB_TOKEN` để push GHCR; không tự tạo secret này |
| Render → Registry Credentials, nếu image private | GitHub username + classic PAT có `read:packages` và quyền đọc package |

Bạn **không cần chép env ứng dụng vào GitHub Actions**. Workflow hiện tại không kết nối DB/Redis production trong lúc build. Test Chroma dùng dữ liệu giả, không gọi embedding API. Token đọc image private là credential của Render, khác deploy hook và khác runtime env BE.

## 1. Chuẩn bị service Python hiện tại

1. Mở đúng service BE trên Render. Lưu lại cấu hình Source, branch, build/start commands, env và thông tin disk hiện có để có thể quay lại.
2. Trong Environment, giữ nguyên `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY` và các secrets đang chạy tốt. Giữ provider/model/dimensions/collection embedding khi tái sử dụng Chroma cũ.
3. Tắt Auto-Deploy của service native trong lúc chuyển để push chuẩn bị không tự restart service cũ.
4. Nếu có dữ liệu Chroma cần giữ, sao lưu nhất quán **toàn bộ thư mục Chroma đang dùng** trước khi thay source, thêm disk hoặc deploy. Các thao tác đó có thể restart service và mất dữ liệu nằm ngoài persistent disk. Xem [cách chuyển Chroma và backup](render-docker-deploy.md#chuyển-dữ-liệu-chroma-cũ-và-backup).

Đổi từ Python sang Docker không tự chuyển dữ liệu từ filesystem cũ vào disk. Nếu chỉ cần tái tạo index từ FAQ/catalog, có thể ingest lại; dữ liệu chỉ tồn tại trong Chroma cần bản sao riêng.

## 2. Build image lần đầu, chưa gọi Render

1. Đưa Dockerfile, entrypoint, requirements, tests và workflow mới lên nhánh `release`. Workflow chạy thủ công cần tồn tại trên default branch của repository để GitHub hiển thị `Run workflow`; nhánh `release` cũng phải có đầy đủ các file mới.
2. Mở GitHub → repository → **Actions → Build Docker and deploy Render → Run workflow**.
3. Chọn branch **release**, bỏ chọn checkbox **Deploy to Render (disable for first image build)** (`deploy=false`), rồi chạy.
4. Đợi job thành công và kiểm tra package/image đã có tại:

   ```text
   ghcr.io/duyaivy/restaurantbe:release
   ```

Nếu push lên `release` trước khi có hook, lượt chạy tự động sẽ fail với thông báo thiếu `RENDER_DEPLOY_HOOK_URL`. Đây là lý do lần đầu cần chạy thủ công với deploy tắt. Nếu đã có hook của service native cũ, vẫn dùng `deploy=false` cho lượt build đầu và cập nhật lại hook sau bước chuyển source.

Nếu repo được fork hoặc đổi tên, workflow dùng `ghcr.io/<owner>/<repo>` viết thường. URL trên Render phải khớp URL workflow publish. Image được build cho `linux/amd64` theo yêu cầu Render.

## 3. Cho Render đọc image GHCR

Package public: Render có thể pull image mà không cần registry credential.

Package private: tạo GitHub classic PAT với `read:packages`, dùng tài khoản có quyền đọc package (và SSO nếu tổ chức yêu cầu). Thêm credential GHCR ở Workspace Settings của Render, rồi chọn credential đó khi đổi Source. Không đưa PAT này vào image hoặc env ứng dụng. Workflow push dùng GITHUB_TOKEN và quyền `packages: write` đã khai báo trong YAML.

## 4. Đổi Source trên service hiện tại

Theo [hướng dẫn đổi runtime của Render](https://render.com/docs/native-runtimes), đường dẫn là **service → Settings → Build → Source → Edit**.

1. Mở **Update Source**, chọn nguồn **Docker image / Existing Image** thay cho repository Python; tên nhãn có thể khác theo giao diện Dashboard.
2. Nhập image URL `ghcr.io/duyaivy/restaurantbe:release`, chọn credential nếu private.
3. Mục tiêu cuối là runtime **image**: Render pull image do GitHub build. Nếu bạn chọn repository và runtime **Docker**, Render sẽ tự build Dockerfile, khác với workflow đã cấu hình.
4. Bỏ build/start commands của native Python khỏi cấu hình nguồn mới. Để **Docker Command** trống, dùng entrypoint của image. Entrypoint tự migrate, collectstatic và chạy Uvicorn.
5. Kiểm tra Environment và Disk trước khi bấm **Deploy**. Khi đổi ngay trên service cũ, rà lại env hiện có; không cần nhập lại toàn bộ env chỉ vì chuyển sang Docker.

Thay `render.yaml` trong repo không tự sửa một service được tạo thủ công trên Dashboard. Nếu service đã được Blueprint quản lý, Render cũng hỗ trợ đổi runtime qua Blueprint rồi sync, nhưng cần rà image credentials, tên service, env và disk trong bản preview thay đổi trước khi áp dụng. Với service hiện tại, làm qua Dashboard sẽ dễ kiểm soát hơn.

Nếu Update Source không cho chọn Docker image trên tài khoản của bạn, dùng **New → Web Service → Existing Image**, tạo service mới và làm các bước cấu hình bên dưới. Khi đó cần import env từ service cũ, copy secret files và chuyển dữ liệu Chroma riêng; URL `.onrender.com` mới sẽ khác. Chỉ chuyển frontend/custom domain sau khi service mới hoạt động.

## 5. Rà env và persistent disk

Trên service chạy image, đặt hoặc kiểm tra:

```dotenv
DJANGO_SETTINGS_MODULE=restaurantBE.settings.production
ENV=prod
PORT=10000
WEB_CONCURRENCY=1
LOG_LEVEL=info
CHATBOT_CHROMA_DIR=/var/data/chroma
```

Các nhóm env DB, Redis, payment, upload, AI vẫn giữ giá trị đang hoạt động. Bảng đầy đủ ở [hướng dẫn env runtime](render-docker-deploy.md#biến-môi-trường-runtime). Giữ nguyên `CHATBOT_CHROMA_COLLECTION`, provider/model/dimensions để đọc index cũ.

- **Disk**: dùng paid compute, gắn persistent disk 1 GB tại `/var/data/chroma`. Gói free không hỗ trợ disk. Nếu đã có disk tại path này, giữ disk hiện tại; nếu disk ở path khác, dùng CHATBOT_CHROMA_DIR nằm bên trong mount path đó hoặc chuyển dữ liệu có kiểm soát.
- **Health Check Path**: `/health/`.
- **Google credentials**: giữ `GOOGLE_CREDENTIALS_JSON_BASE64` nếu đang dùng. Nếu dùng Secret File, xác nhận file còn tồn tại và `GOOGLE_APPLICATION_CREDENTIALS` trỏ `/etc/secrets/<tên-file>`; path của native source hoặc path máy local không dùng được trong Docker.
- **PYTHON_VERSION**: image dùng Python 3.11 từ Dockerfile, biến này không điều khiển Python trong container.
- **URL**: đổi ngay trên service hiện tại thì kiểm tra URL sau chuyển. Nếu tạo service mới, cập nhật HOST, ALLOWED_HOSTS, VNPay return URL và URL BE bên frontend theo URL/domain mới; CORS_ALLOWED_ORIGINS vẫn là origin FE.

Disk giữ dữ liệu qua deploy/restart, nhưng chỉ hỗ trợ một instance và có gián đoạn ngắn khi deploy. Không có disk thì dùng Docker cũng vẫn mất DB local. [Tài liệu persistent disk](https://render.com/docs/disks)

## 6. Nối GitHub Actions vào service chạy image

1. Sau khi source đã là image, mở **Settings → Deploy Hook** của đúng service đó và copy URL hiện tại.
2. Trong GitHub → repository → **Settings → Secrets and variables → Actions → New repository secret**, tạo/cập nhật:

   ```text
   Name: RENDER_DEPLOY_HOOK_URL
   Secret: <deploy hook URL của service chạy image>
   ```

3. Không dùng hook của service native khác. Nếu đổi ngay service hiện tại, copy lại hook trong Dashboard để xác nhận đang trỏ đúng service; không giả định URL hook bắt buộc thay đổi.
4. Chạy workflow thủ công trên `release` với `deploy=true`, hoặc push commit tiếp theo lên `release`.

Workflow push image đã test với tag `release` và tag theo commit, lấy digest rồi gọi deploy hook bằng `imgURL`. Render pull đúng digest đó. Push tag GHCR một mình không tự kích hoạt deploy Render. Hook chấp nhận yêu cầu không có nghĩa app đã lên thành công; xem Events và Logs của Render. [Cách deploy prebuilt image](https://render.com/docs/deploying-an-image)

## 7. Xác nhận chuyển thành công

1. Trong Render, deploy mới có trạng thái **Live**. Log có migrate, collectstatic và Uvicorn bind `0.0.0.0:10000`.
2. Gọi health bằng URL BE thực:

   ```bash
   curl --fail https://TEN-SERVICE.onrender.com/health/
   ```

   Kết quả cần có `"status": "ok"`, `"db": "ok"`, `"redis": "ok"` và `"chroma_storage": "ok"`. Endpoint trả 503 nếu một dependency lỗi.
3. Kiểm tra API có xác thực, Socket.IO/Redis, upload Cloudinary, chatbot và luồng VNPay sandbox theo cấu hình của bạn. Không thực hiện giao dịch thật để test deploy.
4. Nếu đã chuyển dữ liệu Chroma, thử đọc dữ liệu cũ. Redeploy một lần nữa và kiểm tra dữ liệu vẫn còn để xác nhận mount/path đúng.

Khi cần quay lại: service đổi trực tiếp có thể đổi Source về repository/branch Python và khôi phục commands đã lưu. Với service mới, có thể chuyển frontend/domain về service cũ. Các thao tác đổi nguồn không rollback migration PostgreSQL; cần xem xét migration riêng khi đổi phiên bản code.

## Nếu health check trả 400 sau khi đổi sang image

Nếu log đã có `Uvicorn running on http://0.0.0.0:10000` nhưng `/health/` trả 400, kiểm tra `ALLOWED_HOSTS` trước. Giá trị env chỉ gồm hostname, phân cách bằng dấu phẩy; không có `https://`, đường dẫn `/`, dấu ngoặc danh sách hoặc dấu nháy được nhập trực tiếp trong Dashboard.

```dotenv
ALLOWED_HOSTS=.onrender.com,localhost,127.0.0.1
```

Nếu có custom domain BE, thêm domain đó vào danh sách, ví dụ `api.example.com`. Render gửi health check bằng custom domain đã xác minh hoặc hostname service; địa chỉ `10.x` trong access log là IP của client gửi probe, không phải hostname cần thêm vào ALLOWED_HOSTS. [Render health checks](https://render.com/docs/health-checks)

Sau khi sửa env, lưu và redeploy service. Image đã publish trước khi sửa code vẫn cần env đúng. Settings production mới sẽ bỏ khoảng trắng, bỏ phần tử rỗng và tự thêm `RENDER_EXTERNAL_HOSTNAME` do Render cấp, cùng localhost/127.0.0.1; custom domain vẫn cần khai báo riêng. Muốn dùng sửa code này cần push lên `release` để build/publish/deploy image mới.

`HOST` là URL đầy đủ dùng cho schema/API, không thay thế `ALLOWED_HOSTS`. Cảnh báo `dishes` có model changes chưa có migration và thông báo ASGI lifespan không phải nguyên nhân của health check 400.

## Đọc log health check trên Render

Đặt `LOG_LEVEL=info`, deploy image mới, rồi mở Logs của service. Mỗi health check có thời gian, logger, Host, HTTP status, trạng thái từng dependency và latency:

```text
INFO [restaurantBE.health] Health check: method=GET host=my-api.onrender.com status=200 db=ok redis=ok chroma_storage=ok elapsed_ms=21.3
ERROR [restaurantBE.health] Health check failed: component=redis exception=ConnectionError reason=Connection refused elapsed_ms=3.1
ERROR [restaurantBE.health] Health check: method=GET host=my-api.onrender.com status=503 db=ok redis=error chroma_storage=ok elapsed_ms=24.0
```

`db`: thực hiện SELECT 1 để phát hiện cả connection cũ đã đứt. `redis`: PING với timeout 3 giây cho connect/read và không retry trong probe. `chroma_storage`: ghi/xóa file tạm ở CHATBOT_CHROMA_DIR để phát hiện không có quyền ghi hoặc đầy disk. Kiểm tra storage không đọc index hoặc gọi model API, và không chứng minh disk persistent đã được gắn. PostgreSQL connect_timeout mặc định production là 5 giây, trừ khi DATABASE_URL đã khai báo khác.

Health trả 200 khi tất cả thành công, 503 nếu DB/Redis/storage lỗi. JSON chỉ chứa trạng thái, không trả exception/credentials ra public; lỗi cụ thể nằm trong log với exception type và message đã che secrets. Health endpoint không kiểm tra quota/availability của Groq/Jina, vì gọi AI API liên tục từ health check sẽ tiêu tốn quota.

Với 400, tìm logger `django.security.DisallowedHost`: Django từ chối Host trước khi health view chạy, nên không có dòng Health check của request đó. Cấu hình production mới ghi cả lỗi này ra console. Không cần bật DEBUG để xem lỗi.
