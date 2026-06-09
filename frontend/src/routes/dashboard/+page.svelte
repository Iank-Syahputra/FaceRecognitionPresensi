<script lang="ts">
  import { onMount } from 'svelte';

  let courses: any[] = $state([]);
  let isLoading = $state(true);

  async function loadData() {
    isLoading = true;
    try {
      const response = await fetch('http://localhost:8000/api/courses');
      if (response.ok) {
        const result = await response.json();
        courses = result.data;
      }
    } catch (err) {
      console.error(err);
      alert("Gagal memuat daftar mata kuliah dari server.");
    } finally {
      isLoading = false;
    }
  }

  onMount(() => {
    loadData();
  });

  async function startSession(courseId: string) {
    try {
      const response = await fetch('http://localhost:8000/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ course_id: courseId })
      });
      if (response.ok) {
        const result = await response.json();
        const sessionId = result.data.id;
        const courseName = result.course_name;
        window.location.href = `/scan?session_id=${sessionId}&course=${encodeURIComponent(courseName)}`;
      } else {
        alert("Gagal membuat sesi kelas baru.");
      }
    } catch (err) {
      alert("Terjadi kesalahan jaringan.");
    }
  }

  async function deleteSession(sessionId: string) {
    if (confirm("Hapus riwayat presensi ini secara permanen? Seluruh data kehadiran pada tanggal ini akan hilang.")) {
      try {
        const response = await fetch(`http://localhost:8000/api/sessions/${sessionId}`, {
          method: 'DELETE'
        });
        if (response.ok) {
          // Muat ulang data setelah dihapus
          await loadData();
        } else {
          alert("Gagal menghapus riwayat.");
        }
      } catch (err) {
        alert("Terjadi kesalahan jaringan.");
      }
    }
  }

  function formatDateTime(isoString: string) {
    const date = new Date(isoString);
    return date.toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  }
</script>

<div class="min-h-screen bg-slate-50 py-10 px-4 sm:px-6 lg:px-8">
  <div class="max-w-7xl mx-auto">
    
    <div class="flex justify-between items-center mb-8 bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <div>
        <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">Dashboard Dosen</h1>
        <p class="text-gray-500 mt-1">Pilih mata kuliah untuk absen hari ini, atau pantau riwayat kehadiran sebelumnya.</p>
      </div>
      <a href="/" class="px-4 py-2 bg-slate-100 text-slate-700 font-bold rounded-lg hover:bg-slate-200 transition-colors">
        &larr; Menu Utama
      </a>
    </div>

    {#if isLoading}
      <div class="flex flex-col items-center justify-center py-20">
        <div class="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
        <p class="mt-4 text-gray-500 font-medium">Memuat data SIAKAD...</p>
      </div>
    {:else if courses.length === 0}
      <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-md">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-yellow-700 font-medium">
              Belum ada Mata Kuliah di Database.
            </p>
          </div>
        </div>
      </div>
    {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {#each courses as course}
          <div class="bg-white rounded-2xl shadow-md border border-gray-100 overflow-hidden hover:shadow-lg transition-shadow duration-300 flex flex-col h-[500px]">
            
            <!-- Header Card Mata Kuliah -->
            <div class="bg-indigo-600 p-5 shrink-0">
              <div class="flex justify-between items-start mb-2">
                <span class="bg-white/20 text-indigo-50 text-xs font-bold px-2.5 py-1 rounded-md tracking-wider uppercase inline-block">
                  {course.course_code}
                </span>
                <span class="text-indigo-200 text-xs font-medium bg-black/20 px-2 py-1 rounded-md">
                  {course.course_sessions ? course.course_sessions.length : 0} Pertemuan
                </span>
              </div>
              <h2 class="text-xl font-bold text-white leading-tight line-clamp-2" title={course.course_name}>
                {course.course_name}
              </h2>
              <p class="text-sm text-indigo-200 font-medium mt-2 flex items-center gap-1.5">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                {course.lecturer_name}
              </p>
            </div>
            
            <!-- Area Riwayat Sesi (Scrollable) -->
            <div class="flex-1 overflow-y-auto p-4 bg-slate-50/50">
              {#if !course.course_sessions || course.course_sessions.length === 0}
                <div class="h-full flex flex-col items-center justify-center text-center opacity-60">
                  <svg class="w-10 h-10 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                  <p class="text-sm font-medium text-gray-500">Belum ada riwayat kelas.</p>
                </div>
              {:else}
                <div class="space-y-3">
                  {#each course.course_sessions as session}
                    <div class="bg-white border border-gray-200 rounded-lg p-3 flex justify-between items-center group relative shadow-sm">
                      <div class="flex-1">
                        <div class="flex items-center gap-2 mb-1">
                          {#if session.status === 'active'}
                            <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                            <span class="text-xs font-bold text-green-600 uppercase tracking-wide">Sedang Berlangsung</span>
                          {:else}
                            <span class="w-2 h-2 rounded-full bg-gray-400"></span>
                            <span class="text-xs font-bold text-gray-500 uppercase tracking-wide">Selesai</span>
                          {/if}
                        </div>
                        <p class="text-sm font-bold text-gray-800">{formatDateTime(session.created_at)}</p>
                        <p class="text-xs font-medium text-indigo-600 mt-1 flex items-center gap-1">
                          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
                          {session.attendance_count} Hadir
                        </p>
                      </div>
                      
                      <!-- Tombol Lanjutkan & Hapus -->
                      <div class="flex flex-col items-end gap-2">
                        {#if session.status === 'active'}
                          <button onclick={() => window.location.href = `/scan?session_id=${session.id}&course=${encodeURIComponent(course.course_name)}`} class="text-xs font-bold bg-indigo-100 text-indigo-700 px-3 py-1.5 rounded-md hover:bg-indigo-200">
                            Buka Layar
                          </button>
                        {:else}
                          <button onclick={() => window.location.href = `/session/${session.id}`} class="text-xs font-bold bg-gray-100 text-gray-700 px-3 py-1.5 rounded-md hover:bg-gray-200 flex items-center gap-1">
                            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                            Lihat Detail
                          </button>
                        {/if}
                        <button onclick={() => deleteSession(session.id)} class="text-gray-400 hover:text-red-500 transition-colors p-1 opacity-0 group-hover:opacity-100" title="Hapus Riwayat">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                        </button>
                      </div>
                    </div>
                  {/each}
                </div>
              {/if}
            </div>

            <!-- Tombol Buka Sesi Baru -->
            <div class="p-4 bg-white border-t border-gray-100 shrink-0">
              <button 
                onclick={() => startSession(course.id)}
                class="w-full py-3 bg-indigo-50 text-indigo-700 font-bold rounded-xl hover:bg-indigo-600 hover:text-white border border-indigo-100 hover:border-indigo-600 transition-all duration-200 flex items-center justify-center gap-2"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
                Buat Sesi Kelas Hari Ini
              </button>
            </div>
            
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>
