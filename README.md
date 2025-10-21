# Note API 文档

代码参考：
- 主入口与路由：`main.py`
- 数据模型：`models.py`

## 基础信息
- Base URL: `http://127.0.0.1:8000`
- 认证：无
- CORS：已开启（允许所有来源、方法、Headers）
- 内容类型：
  - JSON 请求/响应用于笔记相关接口
  - multipart/form-data 用于图片上传
- 时间字段格式：ISO8601 字符串（FastAPI 默认）

## 数据模型

### NoteIn（请求模型，用于创建笔记）
- title: string
- content: string

示例：
```json
{
  "title": "My first note",
  "content": "Hello world"
}
```

### NoteOut（响应模型，用于返回笔记）
- id: string（MongoDB `_id` 的字符串）
- title: string
- content: string
- images: string[]（图片 id 列表，默认空数组）
- created_at: string（ISO8601）
- updated_at: string（ISO8601）

示例：
```json
{
  "id": "6635f0c2e6d9f0e8b1c1a111",
  "title": "My first note",
  "content": "Hello world",
  "images": [],
  "created_at": "2025-01-01T12:34:56.789000",
  "updated_at": "2025-01-01T12:34:56.789000"
}
```

## 接口列表

### 1) 创建笔记
- Method: `POST`
- Path: `/notes`
- Request Body: `NoteIn`（JSON）
- Response: `200 OK`，`NoteOut`
- 错误：`422 Unprocessable Entity`（字段缺失或类型不匹配）

请求示例：
```bash
curl -X POST http://127.0.0.1:8000/notes \
  -H "Content-Type: application/json" \
  -d '{"title":"My first note","content":"Hello world"}'
```

响应示例：
```json
{
  "id": "6635f0c2e6d9f0e8b1c1a111",
  "title": "My first note",
  "content": "Hello world",
  "images": [],
  "created_at": "2025-01-01T12:34:56.789000",
  "updated_at": "2025-01-01T12:34:56.789000"
}
```

---

### 2) 列出笔记
- Method: `GET`
- Path: `/notes`
- Response: `200 OK`，`List<NoteOut>`

请求示例：
```bash
curl http://127.0.0.1:8000/notes
```

响应示例：
```json
[
  {
    "id": "6635f0c2e6d9f0e8b1c1a111",
    "title": "My first note",
    "content": "Hello world",
    "images": [],
    "created_at": "2025-01-01T12:34:56.789000",
    "updated_at": "2025-01-01T12:34:56.789000"
  }
]
```

---

### 3) 获取单条笔记
- Method: `GET`
- Path: `/notes/{id}`
- Path Params：
  - id: string（笔记 id）
- Response：
  - `200 OK`，`NoteOut`
  - `404 Not Found`（找不到笔记）

请求示例：
```bash
curl http://127.0.0.1:8000/notes/6635f0c2e6d9f0e8b1c1a111
```

成功响应示例：
```json
{
  "id": "6635f0c2e6d9f0e8b1c1a111",
  "title": "My first note",
  "content": "Hello world",
  "images": [],
  "created_at": "2025-01-01T12:34:56.789000",
  "updated_at": "2025-01-01T12:34:56.789000"
}
```

404 响应示例：
```json
{ "detail": "Note not found" }
```

---

### 4) 上传图片（GridFS）
- Method: `POST`
- Path: `/upload-image`
- Request：`multipart/form-data`，字段名 `file`
- Response：`200 OK`
  - 字段：`image_id`（GridFS 文件 id）

前端示例（fetch）：
```javascript
const form = new FormData();
form.append("file", fileInput.files[0]); // <input type="file" id="fileInput">

const res = await fetch("http://127.0.0.1:8000/upload-image", {
  method: "POST",
  body: form
});
const data = await res.json(); // { image_id: "..." }
```

响应示例：
```json
{
  "image_id": "6635f1a9e6d9f0e8b1c1a222"
}
```

说明：服务器会将文件的 `content-type` 写入 GridFS 的 `metadata`，下载时用于返回正确的 `Content-Type`。

---

### 5) 获取图片
- Method: `GET`
- Path: `/image/{image_id}`
- Path Params：
  - image_id: string（GridFS 文件 id）
- Response：
  - `200 OK`，二进制文件流，`Content-Type` 来自文件 metadata（如无则为 `application/octet-stream`）
  - `404 Not Found`（找不到图片）

直接作为图片 src：
```html
<img src="http://127.0.0.1:8000/image/IMAGE_ID" />
```

使用 fetch 读取 Blob：
```javascript
const res = await fetch("http://127.0.0.1:8000/image/IMAGE_ID");
if (!res.ok) throw new Error("Image not found");
const blob = await res.blob();
const url = URL.createObjectURL(blob);
document.querySelector("img").src = url;
```

### 6) 更新笔记（部分更新）
- Method: `PATCH`
- Path: `/notes/{id}`
- Request Body: `NoteUpdate`（JSON，可选字段）
  - title?: string
  - content?: string
- Response: `200 OK`，`NoteOut`
- 错误：
  - `404 Not Found`（笔记不存在）
  - `422 Unprocessable Entity`（请求体验证失败）

请求示例：
```bash
curl -X PATCH http://127.0.0.1:8000/notes/NOTE_ID \
  -H "Content-Type: application/json" \
  -d '{"title":"updated title"}'
```

### 7) 删除笔记
- Method: `DELETE`
- Path: `/notes/{id}`
- Response：
  - `204 No Content`（删除成功）
  - `404 Not Found`（笔记不存在）

请求示例：
```bash
curl -X DELETE http://127.0.0.1:8000/notes/NOTE_ID -i
```

### 8) 为笔记追加图片
- Method: `POST`
- Path: `/notes/{id}/images`
- Request Body: `ImagesAppend`
  - image_ids: string[]（要追加的图片 id 列表）
- 行为：使用 `$addToSet` + `$each` 去重追加到 `images` 数组
- Response：`200 OK`，`NoteOut`
- 错误：
  - `404 Not Found`（笔记不存在）
  - `422 Unprocessable Entity`（image_ids 为空）

请求示例：
```bash
curl -X POST http://127.0.0.1:8000/notes/NOTE_ID/images \
  -H "Content-Type: application/json" \
  -d '{"image_ids":["6635f1a9e6d9f0e8b1c1a222","6635f1a9e6d9f0e8b1c1a333"]}'
```

## 注意与限制（已更新）
- 已提供更新（PATCH）与删除（DELETE）接口；更新为部分更新，自动维护 `updated_at`。
- 已提供为笔记追加图片的接口；图片 id 存储在笔记的 `images` 数组中，并通过 `$addToSet` 去重。
- 错误响应结构使用 FastAPI 默认格式，例如：
```json
{ "detail": "Note not found" }
```