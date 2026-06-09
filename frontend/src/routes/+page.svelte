<script lang="ts">
  // Dashboard Home
</script>

<div class="min-h-screen bg-campus-surface flex flex-col justify-center py-10 px-4 sm:px-6 lg:px-8 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] bg-blend-multiply bg-opacity-20">
  <div class="sm:mx-auto sm:w-full sm:max-w-md animate-fade-in-down">
    <div class="mx-auto w-24 h-24 bg-campus-primary text-white rounded-full flex items-center justify-center shadow-[0_8px_30px_rgb(5,38,89,0.4)] mb-6 ring-4 ring-white/50">
      <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>
    </div>
    <h2 class="text-center text-3xl md:text-4xl font-black text-campus-navy tracking-tight leading-tight">
      Sistem Presensi<br/><span class="text-campus-primary">Biometrik</span>
    </h2>
    <p class="mt-3 text-center text-sm font-bold text-campus-secondary uppercase tracking-widest">
      Universitas Halu Oleo FMIPA Prodi Ilmu Komputer
    </p>
  </div>

  <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-lg">
    <div class="bg-white/90 backdrop-blur-md py-8 px-6 shadow-2xl rounded-3xl border border-white/40">
      
      <div class="space-y-6">
        <!-- Opsi 1: Mahasiswa (Enrollment) -->
        <div class="relative">
          <div class="absolute inset-0 flex items-center" aria-hidden="true">
            <div class="w-full border-t border-campus-muted/30"></div>
          </div>
          <div class="relative flex justify-center">
            <span class="px-4 bg-white text-[10px] font-bold text-campus-muted uppercase tracking-widest rounded-full border border-campus-muted/20">Akses Mahasiswa</span>
          </div>
        </div>

        <a href="/enroll" class="group block relative w-full rounded-2xl border-2 border-dashed border-campus-muted/40 p-6 text-center hover:border-campus-primary hover:bg-campus-surface/30 transition-all duration-300">
          <span class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-campus-surface text-campus-primary group-hover:scale-110 transition-transform duration-300 shadow-sm">
            <svg class="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path></svg>
          </span>
          <span class="mt-4 block text-lg font-bold text-campus-navy">Registrasi Wajah Baru</span>
          <span class="mt-2 block text-sm text-campus-secondary font-medium leading-relaxed">Pendaftaran biometrik mandiri bagi mahasiswa untuk akses SIAKAD.</span>
        </a>

        <!-- Opsi 2: Admin/Dosen (Kiosk Scan) -->
        <div class="relative mt-8">
          <div class="absolute inset-0 flex items-center" aria-hidden="true">
            <div class="w-full border-t border-campus-muted/30"></div>
          </div>
          <div class="relative flex justify-center">
            <span class="px-4 bg-white text-[10px] font-bold text-campus-muted uppercase tracking-widest rounded-full border border-campus-muted/20">Akses Dosen</span>
          </div>
        </div>

        <a href="/dashboard" class="group block w-full p-4 rounded-2xl bg-gradient-to-br from-campus-navy to-campus-primary text-white hover:shadow-lg hover:shadow-campus-primary/30 hover:-translate-y-1 transition-all duration-300">
          <div class="flex items-center gap-4">
            <div class="p-3 bg-white/10 backdrop-blur-sm rounded-xl">
              <svg class="h-6 w-6 text-campus-surface" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
            </div>
            <div class="text-left flex-1">
              <h3 class="text-base font-bold text-white">Dashboard Dosen</h3>
              <p class="text-xs text-campus-surface/80 mt-0.5">Kelola kelas & pantau kehadiran.</p>
            </div>
            <svg class="h-5 w-5 text-campus-surface/50 group-hover:text-white group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
          </div>
        </a>

      </div>
    </div>
  </div>
</div>

<style>
  @keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .animate-fade-in-down {
    animation: fadeInDown 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  }
</style>