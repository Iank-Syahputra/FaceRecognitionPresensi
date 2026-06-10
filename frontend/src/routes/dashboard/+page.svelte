<script lang="ts">
  import { onMount } from 'svelte';

  let courses: any[] = $state([]);
  let isLoading = $state(true);

  // State untuk Modal Tambah Mata Kuliah
  let showAddCourseModal = $state(false);
  let newCourseCode = $state('');
  let newCourseName = $state('');
  let newLecturerName = $state('');
  let isSubmitting = $state(false);

  // State untuk Modal Buat Sesi
  let showCreateSessionModal = $state(false);
  let createSessionCourseId = $state('');
  let createSessionCourseName = $state('');
  let sessionStartAt = $state('');
  let sessionEndAt = $state('');
  let sessionSubmitting = $state(false);

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

  async function addCourse() {
    if (!newCourseCode || !newCourseName || !newLecturerName) {
      return alert("Mohon lengkapi semua data kelas.");
    }

    isSubmitting = true;
    try {
      const response = await fetch('http://localhost:8000/api/courses', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          course_code: newCourseCode,
          course_name: newCourseName,
          lecturer_name: newLecturerName
        })
      });

      if (response.ok) {
        showAddCourseModal = false;
        newCourseCode = '';
        newCourseName = '';
        newLecturerName = '';
        await loadData();
      } else {
        alert("Gagal menambahkan mata kuliah.");
      }
    } catch (err) {
      alert("Terjadi kesalahan jaringan saat menambah kelas.");
    } finally {
      isSubmitting = false;
    }
  }

  function toDateTimeLocal(date: Date) {
    const offsetMs = date.getTimezoneOffset() * 60000;
    return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16);
  }

  function openCreateSessionModal(courseId: string, courseName: string) {
    createSessionCourseId = courseId;
    createSessionCourseName = courseName;

    const now = new Date();
    sessionStartAt = toDateTimeLocal(now);
    sessionEndAt = toDateTimeLocal(new Date(now.getTime() + 60 * 60 * 1000));

    showCreateSessionModal = true;
  }

  async function createSession() {
    if (!createSessionCourseId || !sessionStartAt || !sessionEndAt) {
      return alert("Mohon isi semua data sesi kelas.");
    }
    if (new Date(sessionEndAt) <= new Date(sessionStartAt)) {
      return alert("Waktu selesai harus lebih besar dari waktu mulai.");
    }

    sessionSubmitting = true;
    try {
      const response = await fetch('http://localhost:8000/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          course_id: createSessionCourseId,
          start_at: new Date(sessionStartAt).toISOString(),
          end_at: new Date(sessionEndAt).toISOString()
        })
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
    } finally {
      sessionSubmitting = false;
      showCreateSessionModal = false;
    }
  }

  async function deleteSession(sessionId: string) {
    if (confirm("Hapus riwayat presensi ini secara permanen? Seluruh data kehadiran pada tanggal ini akan hilang.")) {
      try {
        const response = await fetch(`http://localhost:8000/api/sessions/${sessionId}`, {
          method: 'DELETE'
        });
        if (response.ok) {
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

<div class="min-h-screen bg-campus-surface pb-10">
  <header class="bg-campus-navy text-white px-4 py-4 sm:px-6 shadow-md flex items-center justify-between sticky top-0 z-10">
    <div class="flex items-center gap-3">
      <a href="/" class="p-2 bg-white/10 rounded-full hover:bg-white/20 transition-colors">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
      </a>
      <div>
        <h1 class="text-xl font-bold tracking-tight">Dashboard Dosen</h1>
        <p class="text-xs text-campus-surface/70 hidden sm:block">Kelola sesi kelas & pantau kehadiran</p>
      </div>
    </div>

    <button onclick={() => showAddCourseModal = true} class="flex items-center gap-2 bg-campus-primary hover:bg-campus-surface hover:text-campus-navy border border-campus-surface/20 text-white px-4 py-2 rounded-xl transition-all text-sm font-bold shadow-sm group">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
      <span class="hidden sm:block">Tambah Kelas</span>
    </button>
  </header>

  <div class="max-w-7xl mx-auto mt-6 px-4">
    {#if isLoading}
      <div class="flex flex-col items-center justify-center py-20 bg-white/50 backdrop-blur-sm rounded-3xl border border-white/50 shadow-xl">
        <div class="w-12 h-12 border-4 border-campus-surface border-t-campus-primary rounded-full animate-spin"></div>
        <p class="mt-4 text-campus-navy font-bold">Memuat data SIAKAD...</p>
      </div>
    {:else if courses.length === 0}
      <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-xl shadow-sm">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-yellow-700 font-bold">
              Belum ada Mata Kuliah di Database. Silakan tambah kelas baru.
            </p>
          </div>
        </div>
      </div>
    {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 lg:gap-8">
        {#each courses as course}
          <div class="bg-white rounded-3xl shadow-xl border border-white overflow-hidden hover:shadow-2xl hover:shadow-campus-primary/10 transition-shadow duration-300 flex flex-col h-[500px]">
            <div class="bg-gradient-to-br from-campus-navy to-campus-primary p-6 shrink-0 relative overflow-hidden">
              <div class="absolute -right-6 -top-6 w-24 h-24 bg-white/5 rounded-full blur-2xl"></div>
              <div class="flex justify-between items-start mb-3 relative z-10">
                <span class="bg-campus-surface text-campus-navy text-xs font-black px-3 py-1 rounded-lg tracking-wider uppercase shadow-sm">
                  {course.course_code}
                </span>
                <span class="text-white text-xs font-bold bg-black/30 px-3 py-1 rounded-lg backdrop-blur-md">
                  {course.course_sessions ? course.course_sessions.length : 0} Pertemuan
                </span>
              </div>
              <h2 class="text-2xl font-black text-white leading-tight line-clamp-2 relative z-10" title={course.course_name}>
                {course.course_name}
              </h2>
              <p class="text-sm text-campus-surface/80 font-medium mt-3 flex items-center gap-2 relative z-10">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                {course.lecturer_name}
              </p>
            </div>

            <div class="flex-1 overflow-y-auto p-4 sm:p-5 bg-slate-50/50">
              {#if !course.course_sessions || course.course_sessions.length === 0}
                <div class="h-full flex flex-col items-center justify-center text-center opacity-50">
                  <svg class="w-12 h-12 text-campus-muted mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                  <p class="text-sm font-bold text-campus-navy">Belum ada riwayat kelas.</p>
                </div>
              {:else}
                <div class="space-y-3">
                  {#each course.course_sessions as session}
                    <div class="bg-white border-2 border-campus-muted/10 rounded-2xl p-4 flex justify-between items-center group relative shadow-sm hover:border-campus-primary/30 transition-colors">
                      <div class="flex-1 min-w-0 pr-2">
                        <div class="flex items-center gap-2 mb-1.5">
                          {#if session.status === 'active'}
                            <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.8)]"></span>
                            <span class="text-[10px] font-black text-emerald-600 uppercase tracking-widest">Sedang Berlangsung</span>
                          {:else}
                            <span class="w-2 h-2 rounded-full bg-campus-muted"></span>
                            <span class="text-[10px] font-bold text-campus-muted uppercase tracking-widest">Selesai</span>
                          {/if}
                        </div>
                        <p class="text-sm font-bold text-campus-navy truncate">{formatDateTime(session.created_at)}</p>
                        {#if session.start_at && session.end_at}
                          <p class="text-xs font-bold text-campus-secondary mt-1">
                            {formatDateTime(session.start_at)} - {formatDateTime(session.end_at)}
                          </p>
                        {:else}
                          <p class="text-xs font-bold text-campus-secondary mt-1">Waktu sesi belum ditentukan</p>
                        {/if}
                        <p class="text-xs font-bold text-campus-secondary mt-1 flex items-center gap-1.5">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
                          {session.attendance_count} Hadir
                        </p>
                      </div>

                      <div class="flex flex-col items-end gap-2 shrink-0">
                        {#if session.status === 'active'}
                          <button onclick={() => window.location.href = `/scan?session_id=${session.id}&course=${encodeURIComponent(course.course_name)}`} class="text-xs font-bold bg-campus-primary text-white px-3 py-1.5 rounded-lg hover:bg-campus-navy shadow-md transition-colors">
                            Buka Layar
                          </button>
                        {:else}
                          <button onclick={() => window.location.href = `/session/${session.id}`} class="text-xs font-bold bg-campus-surface text-campus-primary px-3 py-1.5 rounded-lg hover:bg-campus-secondary hover:text-white transition-colors flex items-center gap-1">
                            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                            Detail
                          </button>
                        {/if}
                        <button onclick={() => deleteSession(session.id)} class="text-campus-muted hover:text-rose-500 transition-colors p-1 opacity-0 lg:opacity-0 lg:group-hover:opacity-100 touch-manipulation:opacity-100" title="Hapus Riwayat">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                        </button>
                      </div>
                    </div>
                  {/each}
                </div>
              {/if}
            </div>

            <div class="p-5 bg-white border-t border-campus-muted/10 shrink-0">
              <button
                onclick={() => openCreateSessionModal(course.id, course.course_name)}
                class="w-full py-3.5 bg-campus-surface text-campus-primary font-bold rounded-2xl hover:bg-campus-primary hover:text-white border-2 border-campus-surface hover:border-campus-primary shadow-sm hover:shadow-lg transition-all duration-300 flex items-center justify-center gap-2 transform active:scale-95"
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

  {#if showCreateSessionModal}
    <div class="fixed inset-0 bg-campus-navy/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
      <div class="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden border border-white">
        <div class="bg-campus-primary p-5 flex justify-between items-center text-white">
          <h2 class="text-xl font-black tracking-tight">Buat Sesi Kelas Hari Ini</h2>
          <button onclick={() => showCreateSessionModal = false} class="p-1 hover:bg-white/20 rounded-full transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <p class="text-sm text-campus-secondary">Mata kuliah: <strong>{createSessionCourseName}</strong></p>
          </div>
          <div>
            <label class="block text-xs font-bold text-campus-secondary uppercase tracking-widest mb-1.5">Mulai</label>
            <input type="datetime-local" bind:value={sessionStartAt} class="block w-full border-2 border-campus-muted/30 rounded-xl bg-campus-surface/20 py-3 px-4 focus:outline-none focus:border-campus-primary font-medium text-campus-navy" />
          </div>
          <div>
            <label class="block text-xs font-bold text-campus-secondary uppercase tracking-widest mb-1.5">Selesai</label>
            <input type="datetime-local" bind:value={sessionEndAt} class="block w-full border-2 border-campus-muted/30 rounded-xl bg-campus-surface/20 py-3 px-4 focus:outline-none focus:border-campus-primary font-medium text-campus-navy" />
          </div>
          <button
            onclick={createSession}
            disabled={sessionSubmitting || !sessionStartAt || !sessionEndAt}
            class="w-full mt-2 py-3.5 bg-campus-primary text-white font-bold rounded-xl hover:bg-campus-navy disabled:bg-campus-muted transition-all shadow-md active:scale-[0.98]"
          >
            {sessionSubmitting ? 'Membuat Sesi...' : 'Buat Sesi Kelas'}
          </button>
        </div>
      </div>
    </div>
  {/if}

  {#if showAddCourseModal}
    <div class="fixed inset-0 bg-campus-navy/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
      <div class="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden border border-white">
        <div class="bg-campus-primary p-5 flex justify-between items-center text-white">
          <h2 class="text-xl font-black tracking-tight">Tambah Mata Kuliah</h2>
          <button onclick={() => showAddCourseModal = false} class="p-1 hover:bg-white/20 rounded-full transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-xs font-bold text-campus-secondary uppercase tracking-widest mb-1.5">Kode Mata Kuliah</label>
            <input type="text" bind:value={newCourseCode} placeholder="Contoh: IF101" class="block w-full border-2 border-campus-muted/30 rounded-xl bg-campus-surface/20 py-3 px-4 focus:outline-none focus:border-campus-primary font-mono text-campus-navy" />
          </div>
          <div>
            <label class="block text-xs font-bold text-campus-secondary uppercase tracking-widest mb-1.5">Nama Mata Kuliah</label>
            <input type="text" bind:value={newCourseName} placeholder="Contoh: Algoritma Lanjut" class="block w-full border-2 border-campus-muted/30 rounded-xl bg-campus-surface/20 py-3 px-4 focus:outline-none focus:border-campus-primary font-medium text-campus-navy" />
          </div>
          <div>
            <label class="block text-xs font-bold text-campus-secondary uppercase tracking-widest mb-1.5">Dosen Pengampu</label>
            <input type="text" bind:value={newLecturerName} placeholder="Contoh: Budi Santoso, M.Kom" class="block w-full border-2 border-campus-muted/30 rounded-xl bg-campus-surface/20 py-3 px-4 focus:outline-none focus:border-campus-primary font-medium text-campus-navy" />
          </div>
          <button
            onclick={addCourse}
            disabled={isSubmitting || !newCourseCode || !newCourseName || !newLecturerName}
            class="w-full mt-2 py-3.5 bg-campus-primary text-white font-bold rounded-xl hover:bg-campus-navy disabled:bg-campus-muted transition-all shadow-md active:scale-[0.98]"
          >
            {isSubmitting ? 'Menyimpan...' : 'Simpan Kelas'}
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
  .animate-fade-in { animation: fadeIn 0.2s ease-out forwards; }
</style>