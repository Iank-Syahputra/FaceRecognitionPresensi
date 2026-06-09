<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';

  let sessionId = $page.params.id;
  let sessionData: any = $state(null);
  let logs: any[] = $state([]);
  let isLoading = $state(true);

  onMount(async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/sessions/${sessionId}/logs`);
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

<div class="min-h-screen bg-slate-50 py-10 px-4 sm:px-6 lg:px-8">
  <div class="max-w-4xl mx-auto">
    
    <div class="flex justify-between items-center mb-6">
      <a href="/dashboard" class="flex items-center gap-2 text-indigo-600 hover:text-indigo-800 font-medium bg-indigo-50 px-4 py-2 rounded-lg transition-colors">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
        Kembali ke Dashboard
      </a>
      
      <button onclick={() => window.print()} class="flex items-center gap-2 bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 shadow-sm font-medium transition-colors">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path></svg>
        Cetak Laporan
      </button>
    </div>

    {#if isLoading}
      <div class="flex flex-col items-center justify-center py-32 bg-white rounded-2xl shadow-sm border border-gray-200">
        <div class="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
        <p class="mt-4 text-gray-500 font-medium">Memuat data absensi...</p>
      </div>
    {:else if sessionData}
      <!-- Header Laporan -->
      <div class="bg-white rounded-2xl shadow-md border border-gray-200 overflow-hidden mb-8">
        <div class="bg-indigo-600 p-6 text-white">
          <div class="flex justify-between items-start mb-2">
            <span class="bg-white/20 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-widest">
              Laporan Kelas
            </span>
            <span class="bg-indigo-800 text-xs font-bold px-3 py-1 rounded-full shadow-inner">
              {logs.length} Mahasiswa Hadir
            </span>
          </div>
          <h1 class="text-3xl font-bold mb-1">{sessionData.courses.course_name}</h1>
          <p class="text-indigo-200">{sessionData.courses.course_code} • {sessionData.courses.lecturer_name}</p>
        </div>
        
        <div class="p-6 bg-slate-50 border-b border-gray-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <p class="text-xs text-gray-500 font-bold uppercase tracking-wider mb-1">Waktu Sesi</p>
            <p class="text-gray-900 font-medium flex items-center gap-2">
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
              {formatDateTime(sessionData.created_at)}
            </p>
          </div>
          <div class="text-left sm:text-right">
             <p class="text-xs text-gray-500 font-bold uppercase tracking-wider mb-1">Status Sesi</p>
             <p class="text-sm font-bold {sessionData.status === 'active' ? 'text-green-600' : 'text-gray-600'} uppercase">
               {sessionData.status === 'active' ? 'Sedang Berlangsung' : 'Telah Ditutup'}
             </p>
          </div>
        </div>
      </div>

      <!-- Tabel Data Hadir -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
        <div class="p-5 border-b border-gray-200">
          <h2 class="text-lg font-bold text-gray-800">Daftar Kehadiran</h2>
        </div>
        
        {#if logs.length === 0}
          <div class="p-12 text-center text-gray-500">
            <svg class="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
            <p class="font-medium text-lg">Belum ada data absensi.</p>
            <p class="text-sm mt-1">Sistem tidak mendeteksi wajah satupun pada sesi ini.</p>
          </div>
        {:else}
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-slate-50 text-gray-500 text-xs uppercase tracking-wider border-b border-gray-200">
                  <th class="px-6 py-4 font-bold">No</th>
                  <th class="px-6 py-4 font-bold">Mahasiswa</th>
                  <th class="px-6 py-4 font-bold">Waktu Scan</th>
                  <th class="px-6 py-4 font-bold">Skor AI</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                {#each logs as log, index}
                  <tr class="hover:bg-slate-50 transition-colors">
                    <td class="px-6 py-4 text-sm text-gray-500 font-medium">
                      {index + 1}
                    </td>
                    <td class="px-6 py-4">
                      <div class="font-bold text-gray-900">{log.students.name}</div>
                      <div class="text-xs text-gray-500 font-mono mt-0.5">{log.students.nim}</div>
                    </td>
                    <td class="px-6 py-4">
                      <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-green-50 text-green-700 text-sm font-bold border border-green-100">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        {formatTime(log.timestamp)}
                      </span>
                    </td>
                    <td class="px-6 py-4">
                      <div class="flex items-center gap-2">
                        <div class="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div class="h-full bg-indigo-500" style="width: {log.similarity_score * 100}%"></div>
                        </div>
                        <span class="text-xs font-bold text-gray-600">{(log.similarity_score * 100).toFixed(1)}%</span>
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
