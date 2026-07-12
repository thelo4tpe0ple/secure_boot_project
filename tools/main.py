import verify
import signer
import parser  # 可选，若没有则直接用 open

FIRMWARE = "../blink/build/blink.bin"
PRIVATE_KEY = "private.pem"
PUBLIC_KEY = "public.pem"
SIG_FILE = "blink.sig"
HASH_FILE = "blink.sha256"

# 1. 读取固件
raw_data = open(FIRMWARE,'rb').read()  # 或直接用 open(FIRMWARE,'rb').read()

# 2. 计算并保存哈希（可选）
digest = verify.compute_sha256(raw_data)
verify.save_digest(digest, HASH_FILE)
print(f"哈希已保存至 {HASH_FILE}")

# 3. 生成签名并保存
signature = signer.sign_data(raw_data, PRIVATE_KEY, key_type='rsa')
signer.save_signature(signature, SIG_FILE)
print(f"签名已保存至 {SIG_FILE}")

# 4. 验证签名（模拟 bootloader）
loaded_sig = open(SIG_FILE, 'rb').read()
ok = verify.verify_signature(raw_data, loaded_sig, PUBLIC_KEY, key_type='rsa')
print("✅ 验证通过" if ok else "❌ 验证失败")