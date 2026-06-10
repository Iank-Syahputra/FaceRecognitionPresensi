<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { API_BASE_URL } from '$lib/api';

  let sessionId = $page.params.id;
  let sessionData: any = $state(null);
  let logs: any[] = $state([]);
  let isLoading = $state(true);

  onMount(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/logs`);
      if (response.ok) {
        const result = await response.json();
        sessionData = result.session;
        logs = result.logs;
      } else {
        alert("Gagal memuat detail sesi atau sesi tidak ditemukan.");
      }
    } catch (err) {
      console.error(err);
      alert("Terjadi kesalahan jaringan.");
    } finally {
      isLoading = false;
    }
  });

  function formatDateTime(isoString: string) {
    const date = new Date(isoString);
    return date.toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  }
  
  function formatTime(isoString: string) {
    const date = new Date(isoString);
    return date.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  }
</script>

<div class="min-h-screen bg-campus-surface pb-10">
  
  <header class="bg-campus-navy text-white px-4 py-4 sm:px-6 shadow-md flex items-center justify-between sticky top-0 z-10">
    <div class="flex items-center gap-4">
      <a href="/dashboard" class="p-2 bg-white/10 rounded-full hover:bg-white/20 transition-colors">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
      </a>
      <h1 class="text-xl font-bold tracking-tight">Detail Kehadiran Mahasiswa</h1>
    </div>
    <button onclick={() => window.print()} class="flex items-center gap-2 bg-white/10 text-white px-4 py-2 rounded-xl hover:bg-white/20 transition-colors text-sm font-bold shadow-sm">
      <svg class="w-4 h-4 hidden sm:block" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path></svg>
      <span>Cetak Laporan</span>
    </button>
  </header>

  <div class="max-w-4xl mx-auto mt-6 px-4 sm:px-6">

    {#if isLoading}
      <div class="flex flex-col items-center justify-center py-20 bg-white/50 backdrop-blur-sm rounded-3xl border border-white/50 shadow-xl">
        <div class="w-12 h-12 border-4 border-campus-surface border-t-campus-primary rounded-full animate-spin"></div>
        <p class="mt-4 text-campus-navy font-bold">Menyiapkan laporan absen...</p>
      </div>
    {:else if sessionData}
      
      <!-- Header Laporan -->
      <div class="bg-white rounded-3xl shadow-xl border border-white overflow-hidden mb-8">
        <div class="bg-gradient-to-br from-campus-primary to-campus-navy p-6 sm:p-8 text-white relative">
          <!-- Decorative element -->
          <div class="absolute -right-10 -top-10 w-40 h-40 bg-white/5 rounded-full blur-3xl"></div>
          
          <div class="flex justify-between items-start mb-4 relative z-10">
            <span class="bg-campus-surface text-campus-navy text-xs font-black px-3 py-1 rounded-lg uppercase tracking-widest shadow-sm">
              Laporan Kelas
            </span>
            <span class="bg-black/30 text-white text-xs font-bold px-3 py-1 rounded-lg backdrop-blur-md">
              {logs.length} Mahasiswa Hadir
            </span>
          </div>
          <h1 class="text-3xl sm:text-4xl font-black mb-2 leading-tight relative z-10">{sessionData.courses.course_name}</h1>
          <p class="text-campus-surface/80 font-medium relative z-10 flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
            {sessionData.courses.lecturer_name}
          </p>
        </div>
        
        <div class="p-6 bg-slate-50/50 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <p class="text-[10px] text-campus-muted font-bold uppercase tracking-widest mb-1">Tanggal Sesi Kelas</p>
            <p class="text-campus-navy font-bold flex items-center gap-2 text-sm">
              <svg class="w-4 h-4 text-campus-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
              {formatDateTime(sessionData.created_at)}
            </p>
          </div>
          <div class="text-left sm:text-right border-t border-campus-muted/10 pt-4 sm:border-0 sm:pt-0">
             <p class="text-[10px] text-campus-muted font-bold uppercase tracking-widest mb-1">Status Kamera</p>
             <p class="text-sm font-black {sessionData.status === 'active' ? 'text-emerald-600' : 'text-rose-600'} uppercase tracking-wide">
               {sessionData.status === 'active' ? 'SEDANG BERJALAN' : 'SESI DITUTUP'}
             </p>
          </div>
        </div>
      </div>

      <!-- Tabel Data Hadir -->
      <div class="bg-white rounded-3xl shadow-xl border border-white overflow-hidden">
        
        {#if logs.length === 0}
          <div class="p-16 text-center">
            <div class="w-20 h-20 bg-campus-surface rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-10 h-10 text-campus-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
            </div>
            <p class="font-bold text-lg text-campus-navy">Tidak ada yang hadir.</p>
            <p class="text-sm text-campus-secondary mt-1">Sistem belum mencatat satu wajah pun pada sesi ini.</p>
          </div>
        {:else}
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-campus-navy text-white text-[10px] uppercase tracking-widest">
                  <th class="px-6 py-4 font-bold rounded-tl-3xl">No</th>
                  <th class="px-6 py-4 font-bold">Identitas Mahasiswa</th>
                  <th class="px-6 py-4 font-bold">Waktu Scan</th>
                  <th class="px-6 py-4 font-bold rounded-tr-3xl">AI Conf</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-campus-muted/10 bg-slate-50/30">
                {#each logs as log, index}
                  <tr class="hover:bg-white transition-colors duration-200 group">
                    <td class="px-6 py-5 text-sm font-black text-campus-muted group-hover:text-campus-primary transition-colors">
                      {index + 1}
                    </td>
                    <td class="px-6 py-5">
                      <div class="font-bold text-campus-navy text-sm md:text-base">{log.students.name}</div>
                      <div class="text-xs text-campus-secondary font-mono mt-1 font-bold">{log.students.nim}</div>
                    </td>
                    <td class="px-6 py-5">
                      <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-700 text-xs font-bold border border-emerald-100 shadow-sm">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        {formatTime(log.timestamp)}
                      </span>
                    </td>
                    <td class="px-6 py-5">
                      <div class="flex items-center gap-3">
                        <span class="text-xs font-black {log.similarity_score > 0.85 ? 'text-emerald-600' : 'text-yellow-600'}">{(log.similarity_score * 100).toFixed(1)}%</span>
                        <div class="w-16 h-1.5 bg-campus-muted/20 rounded-full overflow-hidden hidden sm:block">
                          <div class="h-full rounded-full {log.similarity_score > 0.85 ? 'bg-emerald-500' : 'bg-yellow-500'}" style="width: {log.similarity_score * 100}%"></div>
                        </div>
                      </div>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        {/if}
      </div>
    {/if}
  </div>
</div>