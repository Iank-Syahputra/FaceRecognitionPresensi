<script lang="ts">
  // Dashboard Home
</script>

<div class="min-h-screen bg-slate-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')]">
  <div class="sm:mx-auto sm:w-full sm:max-w-md">
    <div class="mx-auto w-24 h-24 bg-indigo-600 text-white rounded-full flex items-center justify-center shadow-lg mb-4">
      <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>
    </div>
    <h2 class="text-center text-3xl font-extrabold text-gray-900 tracking-tight">
      Sistem Presensi Biometrik
    </h2>
    <p class="mt-2 text-center text-sm text-gray-600 font-medium uppercase tracking-wider">
      Universitas Halu Oleo FMIPA Prodi Ilmu Komputer
    </p>
  </div>

  <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-lg">
    <div class="bg-white py-8 px-4 shadow-xl sm:rounded-2xl sm:px-10 border border-gray-100">
      
      <div class="space-y-6">
        <!-- Opsi 1: Mahasiswa (Enrollment) -->
        <div class="relative">
          <div class="absolute inset-0 flex items-center" aria-hidden="true">
            <div class="w-full border-t border-gray-200"></div>
          </div>
          <div class="relative flex justify-center">
            <span class="px-3 bg-white text-xs font-bold text-gray-500 uppercase tracking-wide">Akses Mahasiswa Baru</span>
          </div>
        </div>

        <a href="/enroll" class="group block relative w-full rounded-xl border-2 border-dashed border-gray-300 p-6 text-center hover:border-indigo-500 hover:bg-indigo-50 transition-all duration-200">
          <span class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-indigo-100 group-hover:bg-indigo-200">
            <svg class="h-6 w-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path></svg>
          </span>
          <span class="mt-4 block text-lg font-bold text-gray-900">Registrasi Wajah (Enrollment)</span>
          <span class="mt-1 block text-sm text-gray-500">Daftarkan biometrik wajah Anda ke dalam pangkalan data universitas untuk pertama kalinya.</span>
        </a>

        <!-- Opsi 2: Admin/Dosen (Kiosk Scan) -->
        <div class="relative mt-8">
          <div class="absolute inset-0 flex items-center" aria-hidden="true">
            <div class="w-full border-t border-gray-200"></div>
          </div>
          <div class="relative flex justify-center">
            <span class="px-3 bg-white text-xs font-bold text-gray-500 uppercase tracking-wide">Akses Dosen & Admin</span>
          </div>
        </div>

        <a href="/dashboard" class="group block w-full flex items-center justify-between p-4 rounded-xl border border-transparent bg-slate-800 text-white hover:bg-slate-900 shadow-md transition-colors duration-200">
          <div class="flex items-center gap-4">
            <div class="p-3 bg-white/10 rounded-lg">
              <svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
            </div>
            <div class="text-left">
              <h3 class="text-base font-bold">Buka Kios Presensi Kelas</h3>
              <p class="text-xs text-slate-300">Pilih mata kuliah dan aktifkan kamera ruang kelas.</p>
            </div>
          </div>
          <svg class="h-5 w-5 text-slate-400 group-hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
        </a>

      </div>
    </div>
  </div>
</div>
