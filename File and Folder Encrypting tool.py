import tkinter as tk
from tkinter import filedialog, messagebox
from cryptography.fernet import Fernet
import shutil
import os
import tempfile

# ---------------- FUNCTIONS ---------------- #

def generate_key():     #generates a cryptographically random 32-byte key, then Base64-encodes it so it's readable as text. Every call produces a completely unique key.
    key = Fernet.generate_key()
    key_entry.delete(0, tk.END)
    key_entry.insert(0, key.decode())  #.decode() converts the key from bytes → string so it can be displayed in the GUI text box.

def encrypt_file():
    file_path = filedialog.askopenfilename()
    if not file_path:
        return

    key = key_entry.get().encode()
    if not key:
        messagebox.showerror("Error", "Enter or generate secret key")
        return

    try:
        fernet = Fernet(key)
        with open(file_path, "rb") as f:
            data = f.read()

        encrypted = fernet.encrypt(data)
        enc_path = file_path + ".secret"

        with open(enc_path, "wb") as ef:
            ef.write(encrypted)

        messagebox.showinfo("Success", f"File encrypted:\n{enc_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Encryption failed: {e}")

def decrypt_file():
    file_path = filedialog.askopenfilename(filetypes=[("Secret Files", "*.secret"), ("All Files", "*.*")])
    if not file_path:
        return

    key = key_entry.get().encode()
    if not key:
        messagebox.showerror("Error", "Enter secret key")
        return

    try:
        fernet = Fernet(key)
        with open(file_path, "rb") as ef:
            encrypted = ef.read()

        decrypted = fernet.decrypt(encrypted)
        out_path = file_path[:-len(".secret")] if file_path.endswith(".secret") else file_path

        if os.path.exists(out_path):
            if not messagebox.askyesno("Confirm Overwrite", f"File already exists:\n{out_path}\n\nOverwrite?"):
                messagebox.showinfo("Cancelled", "Decryption cancelled — file already exists")
                return

        with open(out_path, "wb") as df:
            df.write(decrypted)

        messagebox.showinfo("Success", f"File decrypted:\n{out_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Decryption failed: {e}")

def encrypt_folder():
    folder_path = filedialog.askdirectory()
    if not folder_path:
        return

    key = key_entry.get().encode()
    if not key:
        messagebox.showerror("Error", "Enter or generate secret key")
        return

    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp()
        zip_path = shutil.make_archive(
            os.path.join(temp_dir, "folder"), "zip", folder_path
        )

        fernet = Fernet(key)
        with open(zip_path, "rb") as zf:
            zip_data = zf.read()
        encrypted = fernet.encrypt(zip_data)
        enc_path = folder_path + ".folder.secret"

        with open(enc_path, "wb") as ef:
            ef.write(encrypted)

        messagebox.showinfo("Success", f"Folder encrypted:\n{enc_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Encryption failed: {e}")
    finally:
        if temp_dir is not None:
            shutil.rmtree(temp_dir, ignore_errors=True)

def decrypt_folder():
    file_path = filedialog.askopenfilename(
        filetypes=[("Encrypted Folder", "*.folder.secret"), ("All Files", "*.*")]
    )
    if not file_path:
        return

    key = key_entry.get().encode()
    if not key:
        messagebox.showerror("Error", "Enter secret key")
        return

    temp_dir = None
    try:
        fernet = Fernet(key)
        with open(file_path, "rb") as ef:
            encrypted = ef.read()

        zip_data = fernet.decrypt(encrypted)

        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "folder.zip")

        with open(zip_path, "wb") as zf:
            zf.write(zip_data)

        output_folder = file_path[:-len(".folder.secret")] if file_path.endswith(".folder.secret") else file_path

        if os.path.exists(output_folder):
            if not messagebox.askyesno("Confirm Overwrite", f"Folder already exists:\n{output_folder}\n\nOverwrite?"):
                messagebox.showinfo("Cancelled", "Decryption cancelled — folder already exists")
                return

        os.makedirs(output_folder, exist_ok=True)
        shutil.unpack_archive(zip_path, output_folder)
        messagebox.showinfo("Success", f"Folder decrypted:\n{output_folder}")
    except Exception as e:
        messagebox.showerror("Error", f"Decryption failed: {e}")
    finally:
        if temp_dir is not None:
            shutil.rmtree(temp_dir, ignore_errors=True)

# ---------------- UI ---------------- #

root = tk.Tk()
root.title("File & Folder Encryption Tool")
root.geometry("520x330")
root.resizable(False, False)

tk.Label(root, text="Secret Key (DO NOT LOSE IT)", font=("Arial", 10, "bold")).pack(pady=5)

key_entry = tk.Entry(root, width=65)
key_entry.pack(pady=5)

tk.Button(root, text="Generate Secret Key", command=generate_key).pack(pady=5)

tk.Button(root, text="Encrypt File", width=25, command=encrypt_file).pack(pady=4)
tk.Button(root, text="Decrypt File", width=25, command=decrypt_file).pack(pady=4)

tk.Label(root, text="---------------- Folder Encryption ----------------").pack(pady=5)

tk.Button(root, text="Encrypt Folder", width=25, command=encrypt_folder).pack(pady=4)
tk.Button(root, text="Decrypt Folder", width=25, command=decrypt_folder).pack(pady=4)

root.mainloop()
