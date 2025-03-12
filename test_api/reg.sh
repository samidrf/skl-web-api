curl -X POST http://127.0.0.1:5000/register \
  -H "Content-Type: application/json" \
  -d '{
        "username": "admin123",
        "nama_lengkap": "Tes User",
        "jabatan": "Tester",
        "role": "admin",
        "password": "tes123"
      }'
