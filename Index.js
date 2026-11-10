// ==========================================
// KONFIGURASI ID (Ganti dengan ID milik Anda)
// ==========================================
const SPREADSHEET_ID = "1aGxMB9skYeHrJhXSS12TnZ4S29Y9Om4Ul6Wot4rhhV0";
const GDRIVE_FOLDER_ID = "1z1scCnIPikmE_ynxQGVtqpdM18RwjrN";
const TOKEN_WA_API = "1adfea21b7d0429aa3fb6b88463955fbc5ccde8b52234b0792"; // Contoh: Fonnte, Wablas, dll.

function doGet(e) {
  return HtmlService.createTemplateFromFile('Index')
    .evaluate()
    .setTitle('Portal Astra Daihatsu Karawaci')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

// --- FUNGSI HALAMAN SECURITY ---
function simpanDataSecurity(data) {
  try {
    const sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName("Security");
    const folder = DriveApp.getFolderById(GDRIVE_FOLDER_ID);
    let fotoUrls = [];

    // Proses Multiple Upload Foto ke Google Drive
    if (data.fotos && data.fotos.length > 0) {
      data.fotos.forEach(foto => {
        if (foto.data) {
          let contentType = foto.data.substring(5, foto.data.indexOf(';'));
          let bytes = Utilities.base64Decode(foto.data.substr(foto.data.indexOf('base64,') + 7));
          let blob = Utilities.newBlob(bytes, contentType, foto.name);
          let file = folder.createFile(blob);
          fotoUrls.push(file.getUrl());
        }
      });
    }

    // Simpan ke Excel/Google Sheets
    sheet.appendRow([
      new Date(),
      data.kategori,
      data.merekDaihatsu ? data.tipeDaihatsu : data.tipeManual,
      data.noPolisi,
      data.warna,
      data.namaDriver,
      data.noWa,
      data.keperluan || "-",
      fotoUrls.join("\n") // Gabungkan URL foto
    ]);

    return { status: "success", message: "Data Kendaraan Berhasil Disimpan!" };
  } catch (error) {
    return { status: "error", message: error.toString() };
  }
}

// --- FUNGSI HALAMAN WIP MONITORING ---
function getWipData() {
  const sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName("Data_WIP");
  const data = sheet.getDataRange().getValues();
  const headers = data.shift(); // Buang baris header
  
  return data.map((row, index) => {
    return {
      rowIdx: index + 2,
      noPolisi: row[0] || "-",
      tipe: row[1] || "-",
      warna: row[2] || "-",
      jenisJob: row[3] || "-", // GR atau BR
      namaSA: row[4] || "-",
      aging: row[5] || "-",
      status: row[6] || "-",
      fotoUpdate: row[7] || "-",
      // Field Tambahan Asuransi
      statusSpkAsuransi: row[8] || "-", 
      statusPembayaranOR: row[9] || "-",
      kelengkapanDokumen: row[10] || "-"
    };
  });
}

function updateWipStatus(updateData) {
  try {
    const sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName("Data_WIP");
    const folder = DriveApp.getFolderById(GDRIVE_FOLDER_ID);
    
    // 1. Update cell status umum (Kolom ke-7 / G)
    if (updateData.statusBaru) {
      sheet.getRange(updateData.rowIdx, 7).setValue(updateData.statusBaru);
    }
    
    // 2. Simpan Foto Update jika ada (Kolom ke-8 / H)
    let urlFotoUpdate = "";
    if (updateData.fotoUpdate && updateData.fotoUpdate.data) {
      let contentType = updateData.fotoUpdate.data.substring(5, updateData.fotoUpdate.data.indexOf(';'));
      let bytes = Utilities.base64Decode(updateData.fotoUpdate.data.substr(updateData.fotoUpdate.data.indexOf('base64,') + 7));
      let blob = Utilities.newBlob(bytes, contentType, updateData.fotoUpdate.name);
      let file = folder.createFile(blob);
      urlFotoUpdate = file.getUrl();
      sheet.getRange(updateData.rowIdx, 8).setValue(urlFotoUpdate);
    }

    // 3. Update Status SPK Asuransi (Kolom ke-9 / I)
    if (updateData.statusSpkAsuransi) {
      sheet.getRange(updateData.rowIdx, 9).setValue(updateData.statusSpkAsuransi);
    }

    // 4. Update Status Pembayaran OR (Kolom ke-10 / J)
    if (updateData.statusPembayaranOR) {
      sheet.getRange(updateData.rowIdx, 10).setValue(updateData.statusPembayaranOR);
    }

    // 5. Update Kelengkapan Dokumen Asuransi (Kolom ke-11 / K)
    if (updateData.kelengkapanDokumen) {
      sheet.getRange(updateData.rowIdx, 11).setValue(updateData.kelengkapanDokumen);
    }

    // --- TRIGGER NOTIFIKASI WHATSAPP ---
    // Menyusun pesan secara dinamis, hanya menampilkan data yang diupdate
    let pesanSA = `*Update WIP Karawaci*\nNopol: ${updateData.noPolisi}`;
    if (updateData.statusBaru) pesanSA += `\nStatus Progres: ${updateData.statusBaru}`;
    if (updateData.statusSpkAsuransi) pesanSA += `\nStatus SPK: ${updateData.statusSpkAsuransi}`;
    if (updateData.statusPembayaranOR) pesanSA += `\nPembayaran OR: ${updateData.statusPembayaranOR}`;
    if (updateData.kelengkapanDokumen) pesanSA += `\nDokumen Asuransi: ${updateData.kelengkapanDokumen}`;

    if (updateData.noWaSA) {
      kirimWA(updateData.noWaSA, pesanSA);
    }

    if (updateData.statusBaru === "Tunggu Part") {
      let pesanPart = `*INFO PART DIBUTUHKAN:*\nNopol: ${updateData.noPolisi}\nSA: ${updateData.namaSA}\nMohon admin part segera memproses.`;
      kirimWA("NOMOR_WA_ADMIN_PART", pesanPart); // Ganti dengan nomor WA Admin Part
    }

    return { status: "success", message: "WIP dan Data Asuransi Berhasil Diupdate!" };
  } catch (error) {
    return { status: "error", message: error.toString() };
  }
}

function kirimWA(nomor, pesan) {
  try {
    // Contoh implementasi menggunakan API Fonnte. Sesuaikan jika menggunakan Wablas/lainnya.
    const url = "https://api.fonnte.com/send"; 
    const options = {
      method: "post",
      headers: { "Authorization": TOKEN_WA_API },
      payload: { 
        target: nomor, 
        message: pesan 
      },
      muteHttpExceptions: true // Mencegah script terhenti jika API WA sedang down
    };
    UrlFetchApp.fetch(url, options);
  } catch (error) {
    Logger.log("Gagal mengirim WA: " + error.toString());
  }
}
