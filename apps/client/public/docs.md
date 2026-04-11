# OCR API — Documentation

## Utilisation rapide

Générez un token via la modal **Générer un token** puis utilisez-le dans l'en-tête HTTP :

```
Authorization: Bearer <YOUR_TOKEN>
```

## Exemples

### Bash (curl)

```bash
curl -X POST \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"image_url":"https://example.com/image.png"}' \
  http://localhost:5000/api/ocr
```

### Python (requests)

```python
import requests

resp = requests.post(
    "http://localhost:5000/api/ocr",
    json={"image_url": "https://example.com/image.png"},
    headers={"Authorization": "Bearer <YOUR_TOKEN>", "Content-Type": "application/json"}
)
print(resp.status_code)
print(resp.json())
```

## Notes

- Les tokens dans cette interface sont factices (mock) si vous n'utilisez pas le backend.
- Pour générer les types TypeScript depuis l'OpenAPI, démarrez le backend et utilisez `make generate-openapi`.
