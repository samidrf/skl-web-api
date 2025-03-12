from pydantic import BaseModel, Field, model_validator, ValidationError
from typing import Optional, Literal
from datetime import datetime

class PenggunaCreate(BaseModel):
    username: str
    password: str
    nama_lengkap: str
    jabatan: Optional[str] = "Warga"
    role: Optional[str] = "user"

class SKLCreate(BaseModel):
    nama_anak: str
    jenis_kelamin: Literal['Laki-laki', 'Perempuan']
    anak_ke: int
    tempat_lahir: str
    tanggal_lahir: datetime
    kewarganegaraan: str
    
    # Data Orang Tua
    nik_ayah: str
    nama_ayah: str
    email_ayah: str
    tempat_tanggal_lahir_ayah: str
    pekerjaan_ayah: str
    agama_ayah: str
    alamat_ayah: str
    
    nik_ibu: str
    nama_ibu: str
    email_ibu: str
    tempat_tanggal_lahir_ibu: str
    pekerjaan_ibu: str
    agama_ibu: str
    alamat_ibu: str

class SKLResponse(BaseModel):
    id: int
    nomor_surat: str
    nama_anak: str
    tanggal_surat: datetime
    status: str

class SKLSearch(BaseModel):
    nama_anak: str

class SKLSign(BaseModel):
    nama_anak: str
    email_orang_tua: str