<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { getStoredToken, getStoredUser, authHeaders, clearAuth } from '$lib/auth';

  let videoElement: HTMLVideoElement | undefined = $state();
  let canvasElement: HTMLCanvasElement | undefined = $state();
  let stream: MediaStream | null = $state(null);
  
  let isScanning = $state(false);
  let scanInterval: ReturnType<typeof setInterval>;
  let clockInterval: ReturnType<typeof setInterval>;
  
  let currentTime = $state(new Date());
  let recentLogs: { id: string, name: string, nim: string, time: string, similarity: number }[] = $state([]);
  let currentScannedName: string | null = $state(null);
  
  let sessionId = $state('');
  let courseName = $state('Memuat...');

  onMount(async () => {
    const storedUser = getStoredUser();
    const token = getStoredToken();
    if (!storedUser || !token || storedUser.role !== 'professor') {
      clearAuth();
      window.location.href = '/login';
      return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    sessionId = urlParams.get('session_id') || '';
    courseName = urlParams.get('course') || 'Sesi Tanpa Nama';

    if (!sessionId) {
      alert("Akses ditolak: Sesi kelas tidak ditemukan. Silakan mulai dari Dashboard Dosen.");
      window.location.href = '/dashboard';
      return;
    }

    clockInterval = setInterval(() => {
      currentTime = new Date();
    }, 1000);

    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoElement) {
        videoElement.srcObject = stream;
      }
    } catch (err) {
      console.error("Error camera:", err);
    }
  });

  onDestroy(() => {
    stopScanning();
    clearInterval(clockInterval);
    if (stream) stream.getTracks().forEach(t => t.stop());
  });

  function captureFrame() {
    if (videoElement && canvasElement) {
      const context = canvasElement.getContext('2d');
      if (context) {
        canvasElement.width = videoElement.videoWidth;
        canvasElement.height = videoElement.videoHeight;
        context.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
        return canvasElement.toDataURL('image/jpeg', 0.8);
      }
    }
    return null;
  }

  function startScanning() {
    isScanning = true;
    scanInterval = setInterval(async () => {
      const frame = captureFrame();
      if (!frame) return;

      try {
        const response = await fetch('http://localhost:8000/api/recognize', {
          method: 'POST',
          headers: {
            ...authHeaders(),
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ image: frame, session_id: sessionId })
        });
        
        if (response.ok) {
          const data = await response.json();
          
          if (data.box) {
            faceBox = { 
              x1: data.box[0], y1: data.box[1], 
              x2: data.box[2], y2: data.box[3], 
              show: true 
            };
          }

          if (data.student) {
            liveInfo = {
              name: data.student.name,
              nim: data.student.nim,
              similarity: data.student.similarity,
              threshold: data.threshold,
              match: data.match
            };
          } else {
            liveInfo.name = "Wajah Tidak Dikenal";
            liveInfo.match = false;
            liveInfo.similarity = 0;
          }

          if (data.match && !data.already_logged) {
            currentScannedName = data.student.name;
            setTimeout(() => { currentScannedName = null; }, 3000);

            const newLog = {
              id: crypto.randomUUID(),
              name: data.student.name,
              nim: data.student.nim,
              time: new Date().toLocaleTimeString('id-ID'),
              similarity: data.student.similarity
            };
            recentLogs = [newLog, ...recentLogs];
          }
        } else {
           faceBox.show = false;
        }
      } catch (err) {
        console.error("Scan error:", err);
        faceBox.show = false;
      }
    }, 1000); 
  }

  function stopScanning() {
    isScanning = false;
    clearInterval(scanInterval);
    faceBox.show = false;
    currentScannedName = null;
  }

  function toggleScan() {
    if (isScanning) {
      stopScanning();
    } else {
      startScanning();
    }
  }

  async function closeSession() {
    if (confirm("Tutup sesi kelas ini? Mahasiswa yang telat tidak bisa absen lagi.")) {
      try {
        const response = await fetch(`http://localhost:8000/api/sessions/${sessionId}/close`, {
          method: 'POST',
          headers: authHeaders()
        });
        if (!response.ok) {
          alert('Gagal menutup sesi.');
          return;
        }
        stopScanning();
        if (stream) stream.getTracks().forEach(t => t.stop());
        window.location.href = '/dashboard';
      } catch (err) {
        alert("Gagal menutup sesi.");
      }
    }
  }

  function getBoxStyle(box: typeof faceBox) {
    if (!videoElement || videoElement.videoWidth === 0) return "display: none";
    
    const scaleX = videoElement.clientWidth / videoElement.videoWidth;
    const scaleY = videoElement.clientHeight / videoElement.videoHeight;
    
    const width = (box.x2 - box.x1) * scaleX;
    const height = (box.y2 - box.y1) * scaleY;
    const left = box.x1 * scaleX;
    const top = box.y1 * scaleY;
    
    const mirroredLeft = videoElement.clientWidth - left - width;
    return `left: ${mirroredLeft}px; top: ${top}px; width: ${width}px; height: ${height}px;`;
  }
</script>

<div class="min-h-screen bg-campus-surface flex flex-col">
  
  <header class="bg-campus-navy text-white px-4 py-3 sm:px-6 shadow-md flex items-center justify-between sticky top-0 z-20">
    <div class="flex items-center gap-3">
      <div class="hidden sm:flex w-10 h-10 bg-white/10 rounded-xl items-center justify-center">
        <svg class="w-6 h-6 text-campus-surface" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
      </div>
      <div>
        <h1 class="text-lg sm:text-xl font-bold tracking-tight line-clamp-1">{courseName}</h1>
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full {isScanning ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}"></span>
          <p class="text-[10px] sm:text-xs text-campus-surface/70 uppercase tracking-widest">{isScanning ? 'Kamera Aktif' : 'Kamera Mati'}</p>
        </div>
      </div>
    </div>
    <div class="text-right">
      <div class="text-xl sm:text-2xl font-mono font-bold text-campus-surface">
        {currentTime.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })}
      </div>
    </div>
  </header>

  <main class="flex-1 flex flex-col lg:flex-row p-4 sm:p-6 gap-6 w-full max-w-7xl mx-auto overflow-hidden">
    
    <!-- Kolom Kamera (Lebih kecil dan elegan) -->
    <div class="lg:w-7/12 xl:w-1/2 flex flex-col gap-4">
      <div class="bg-white p-4 rounded-3xl shadow-xl border border-white flex flex-col relative">
        
        <div class="relative w-full aspect-video bg-campus-navy rounded-2xl overflow-hidden shadow-inner flex items-center justify-center border-4 {isScanning ? 'border-emerald-500' : 'border-transparent'} transition-colors duration-500">
          
          {#if !isScanning}
             <div class="absolute inset-0 flex flex-col items-center justify-center text-white/50">
               <svg class="w-16 h-16 mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
               <p class="font-medium tracking-widest uppercase text-sm">Standby Mode</p>
             </div>
          {/if}

          <!-- svelte-ignore a11y_media_has_caption -->
          <video bind:this={videoElement} autoplay playsinline class="absolute inset-0 w-full h-full object-cover transform scale-x-[-1] {isScanning ? 'opacity-100' : 'opacity-30 blur-sm'} transition-all duration-500"></video>
          
          {#if faceBox.show && isScanning}
            <div 
              class="absolute border-[3px] rounded-lg transition-all duration-150 ease-out flex flex-col items-center {liveInfo.match ? 'border-emerald-400 bg-emerald-400/10' : 'border-rose-400 bg-rose-400/10'} shadow-[0_0_15px_rgba(0,0,0,0.3)]"
              style={getBoxStyle(faceBox)}
            >
              <div class="absolute -top-8 bg-campus-navy/90 text-white text-[9px] px-2 py-1 rounded shadow-md whitespace-nowrap flex flex-col items-center backdrop-blur-sm">
                 <span class="font-black tracking-wider {liveInfo.match ? 'text-emerald-400' : 'text-rose-400'}">
                   {liveInfo.match ? 'TERVERIFIKASI' : 'UNKNOWN'}
                 </span>
                 <span class="text-white/80">Sim: {(liveInfo.similarity * 100).toFixed(0)}%</span>
              </div>
              <div class="absolute -bottom-8 bg-campus-primary text-white text-xs font-bold px-3 py-1.5 rounded-full shadow-lg whitespace-nowrap border border-white/20">
                {liveInfo.name}
              </div>
            </div>
          {/if}

          {#if currentScannedName}
            <div class="absolute inset-0 bg-emerald-500/20 backdrop-blur-sm flex items-center justify-center animate-fade-in z-10">
              <div class="bg-white px-6 py-5 rounded-3xl shadow-2xl flex flex-col items-center border-4 border-emerald-500 transform scale-110">
                <div class="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center mb-2 shadow-inner">
                  <svg class="w-8 h-8 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path></svg>
                </div>
                <h3 class="text-lg font-black text-campus-navy text-center line-clamp-1">{currentScannedName}</h3>
                <p class="text-emerald-600 font-bold text-[10px] mt-1 uppercase tracking-widest">Absen Masuk</p>
              </div>
            </div>
          {/if}
        </div>
        <canvas bind:this={canvasElement} class="hidden"></canvas>
      </div>

      <!-- Controls -->
      <div class="bg-white p-4 rounded-3xl shadow-xl border border-white flex justify-between items-center gap-3">
        <button onclick={closeSession} class="px-5 py-3 sm:px-6 bg-rose-50 text-rose-600 font-bold text-sm rounded-2xl hover:bg-rose-100 transition-colors flex-1 sm:flex-none text-center">
          Tutup Sesi
        </button>
        <button 
          onclick={toggleScan} 
          class={`flex-1 py-3 px-4 rounded-2xl font-bold text-sm text-white shadow-lg transition-all duration-300 flex items-center justify-center gap-2 transform active:scale-95 ${isScanning ? 'bg-campus-navy hover:bg-campus-navy/90' : 'bg-campus-primary hover:bg-campus-primary/90'}`}
        >
          {#if isScanning}
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"></path></svg>
            Jeda Kamera
          {:else}
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            Mulai Scan
          {/if}
        </button>
      </div>
    </div>

    <!-- Kolom Log Presensi -->
    <div class="lg:w-5/12 xl:w-1/2 bg-white rounded-3xl shadow-xl border border-white flex flex-col overflow-hidden h-[500px] lg:h-auto">
      <div class="bg-campus-surface/30 border-b border-campus-muted/10 p-5 flex justify-between items-center shrink-0">
        <h2 class="text-lg font-black text-campus-navy">Log Kehadiran</h2>
        <span class="bg-campus-primary text-white text-xs font-bold px-3 py-1 rounded-full shadow-sm">
          {recentLogs.length} Terabsen
        </span>
      </div>
      
      <div class="flex-1 overflow-y-auto p-3 sm:p-5 bg-slate-50/50">
        {#if recentLogs.length === 0}
          <div class="h-full flex flex-col items-center justify-center text-center opacity-50">
            <svg class="w-12 h-12 text-campus-muted mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
            <p class="font-bold text-campus-navy text-sm">Menunggu Mahasiswa...</p>
            <p class="text-xs mt-1 text-campus-secondary">Nyalakan kamera untuk mulai absen.</p>
          </div>
        {:else}
          <div class="space-y-3">
            {#each recentLogs as log (log.id)}
              <div class="bg-white p-3 sm:p-4 rounded-2xl shadow-sm border border-campus-muted/10 flex justify-between items-center animate-fade-in-down hover:border-campus-surface transition-colors">
                <div class="flex items-center gap-3 overflow-hidden">
                   <div class="w-10 h-10 rounded-full bg-campus-surface text-campus-primary flex items-center justify-center shrink-0 font-bold text-sm border border-campus-muted/20">
                     {log.name.charAt(0)}
                   </div>
                   <div class="min-w-0">
                     <p class="text-sm font-bold text-campus-navy truncate">{log.name}</p>
                     <p class="text-[10px] font-mono font-bold text-campus-secondary mt-0.5">{log.nim}</p>
                   </div>
                </div>
                <div class="text-right shrink-0 ml-2">
                  <span class="inline-block px-2 py-1 bg-emerald-50 text-emerald-700 text-[10px] font-black rounded border border-emerald-100 mb-1">
                    {log.time}
                  </span>
                  <p class="text-[9px] text-campus-muted font-bold tracking-wider">MATCH: {(log.similarity * 100).toFixed(0)}%</p>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  </main>
</div>

<style>
  @keyframes fadeInDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
  .animate-fade-in-down { animation: fadeInDown 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
  @keyframes fadeIn { from { opacity: 0; scale: 0.95; } to { opacity: 1; scale: 1; } }
  .animate-fade-in { animation: fadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
</style>