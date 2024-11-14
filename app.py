from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import os

app = Flask(__name__)

# Konfigurasi database
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'banksampa'
app.config['MYSQL_HOST'] = 'localhost'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

mysql = MySQL(app)

# Menampilkan homepage
@app.route("/", methods=["GET", "POST"])
def home():
    try:
        if request.method == "GET":
            # GET: Ambil data dari tabel TPS untuk ditampilkan
            cur = mysql.connection.cursor()
            cur.execute("SELECT idtps, namatps, lokasi, gambar FROM tps")
            data_tps = cur.fetchall()
            cur.close()
            return render_template('index.html', data_tps=data_tps)
        
        elif request.method == "POST":
            # POST: Cek apakah data berasal dari pelaporan atau kritik & saran
            if "namapelapor" in request.form:  # Form pelaporan
                namapelapor = request.form["namapelapor"]
                judullaporan = request.form["judullaporan"]
                isilaporan = request.form["isilaporan"]
                tanggal = request.form["tanggal"]
                nohp_pelapor = request.form["nohp_pelapor"]
                email_pelapor = request.form["email_pelapor"]
                lokasitps = request.form["lokasitps"]

                cur = mysql.connection.cursor()
                sql = """INSERT INTO pelaporan 
                         (namapelapor, judullaporan, isilaporan, tanggal, nohp_pelapor, email_pelapor, lokasitps) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                data = (namapelapor, judullaporan, isilaporan, tanggal, nohp_pelapor, email_pelapor, lokasitps)
                cur.execute(sql, data)
                mysql.connection.commit()
                cur.close()

                return redirect(url_for("home"))

            elif "judulkritik" in request.form:  # Form kritik & saran
                judulkritik = request.form["judulkritik"]
                isikritik = request.form["isikritik"]

                cur = mysql.connection.cursor()
                sql = """INSERT INTO kritiksaran 
                         (judulkritik, isikritik, tglkritik) 
                         VALUES (%s, %s, NOW())"""  # Gunakan NOW() untuk tanggal otomatis
                data = (judulkritik, isikritik)
                cur.execute(sql, data)
                mysql.connection.commit()
                cur.close()

                return redirect(url_for("home"))

        # Jika metode lain (seharusnya tidak terjadi)
        return "Metode tidak didukung.", 405

    except Exception as e:
        return f"Terjadi kesalahan: {e}"



# Menampilkan homepage admin
@app.route("/admin", methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if 'namatps' in request.form and 'lokasi' in request.form and 'gambar' in request.files:
            # Ambil data dari form
            _namatps = request.form['namatps']
            _lokasi = request.form['lokasi']
            _gambar = request.files['gambar']

            # Simpan gambar ke folder uploads
            if _gambar:
                gambar_path = os.path.join(app.config['UPLOAD_FOLDER'], _gambar.filename)
                _gambar.save(gambar_path)

                # Simpan data ke database
                cur = mysql.connection.cursor()
                sql = "INSERT INTO tps (namatps, lokasi, gambar) VALUES (%s, %s, %s)"
                data = (_namatps, _lokasi, _gambar.filename)
                cur.execute(sql, data)
                mysql.connection.commit()
                cur.close()

                return render_template('admin.html', message="TPS berhasil ditambahkan!")
        elif 'idtps' in request.form:
            # Handle delete TPS
            idtps = request.form['idtps']
            cur = mysql.connection.cursor()
            sql = "DELETE FROM tps WHERE idtps = %s"
            cur.execute(sql, (idtps,))
            mysql.connection.commit()
            cur.close()

            return render_template('admin.html', message="TPS berhasil dihapus!")
    return render_template('admin.html')

@app.route("/update_tps", methods=["GET", "POST"])
def update_tps():
    if request.method == "GET":
        # Tampilkan form untuk mengupdate TPS
        return render_template("adminupdate.html")
    
    elif request.method == "POST":
        try:
            # Ambil data dari form
            idtps = request.form.get("idtps")  # ID TPS harus ada
            namatps = request.form.get("namatps")  # Bisa diisi atau dikosongkan
            lokasi = request.form.get("lokasi")  # Bisa diisi atau dikosongkan
            gambar = request.form.get("gambar")  # Bisa diisi atau dikosongkan

            # Update TPS hanya dengan data yang diberikan (tidak null)
            fields_to_update = []
            data_to_update = []

            if namatps:
                fields_to_update.append("namatps = %s")
                data_to_update.append(namatps)

            if lokasi:
                fields_to_update.append("lokasi = %s")
                data_to_update.append(lokasi)

            if gambar:
                fields_to_update.append("gambar = %s")
                data_to_update.append(gambar)

            # Jika tidak ada field untuk diupdate, kembalikan pesan kesalahan
            if not fields_to_update:
                return "Tidak ada data untuk diupdate.", 400

            # Tambahkan ID TPS sebagai syarat di WHERE
            data_to_update.append(idtps)

            # Query update
            query = f"UPDATE tps SET {', '.join(fields_to_update)} WHERE idtps = %s"

            # Eksekusi query
            cur = mysql.connection.cursor()
            cur.execute(query, data_to_update)
            mysql.connection.commit()
            cur.close()

            return render_template("index.html", message="Data TPS berhasil diupdate!")
        except Exception as e:
            return f"Terjadi kesalahan: {e}", 500


# Menampilkan login
@app.route("/login")
def login():
    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)
