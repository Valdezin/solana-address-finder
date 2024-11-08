import cupy as cp
import base58
from nacl.signing import SigningKey
import concurrent.futures
import sys
import time

def generate_address():
 
    signing_key = SigningKey.generate()
    public_key = signing_key.verify_key
    public_key_bytes = public_key.encode()
    solana_address = base58.b58encode(public_key_bytes).decode('utf-8')

    private_key_bytes = signing_key.encode() + public_key_bytes
    solflare_private_key = base58.b58encode(private_key_bytes).decode('utf-8')
    
    return solana_address, solflare_private_key

def generate_random_seeds_on_gpu(batch_size=1000):
 
    random_data = cp.random.randint(0, 256, size=(batch_size, 32), dtype=cp.uint8)
    return cp.asnumpy(random_data)


def find_sol_address_with_prefix(prefix):
    attempt_count = 0
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        while True:
            random_seeds = generate_random_seeds_on_gpu(batch_size=50)

            futures = [executor.submit(generate_address) for seed in random_seeds]

            for future in concurrent.futures.as_completed(futures):
                solana_address, solflare_private_key = future.result()
                attempt_count += 1

                elapsed_time = time.time() - start_time
                sys.stdout.write(f"\rAttempts: {attempt_count} | Time elapsed: {elapsed_time:.2f}s")
                sys.stdout.flush()

                if solana_address.startswith(prefix):
                    print(f"\nFound address: {solana_address}")
                    print(f"Solflare-compatible Private Key (Base58): {solflare_private_key}")
                    print(f"Total Attempts: {attempt_count}")
                    print(f"Time taken: {elapsed_time:.2f} seconds")
                    return

if __name__ == "__main__":
    prefix = input("Enter the desired prefix for the Solana address: ")
    
    if len(prefix) < 1 or len(prefix) > 6:
        print("Please enter a prefix between 1 and 6 characters.")
        sys.exit(1)
    
    find_sol_address_with_prefix(prefix)