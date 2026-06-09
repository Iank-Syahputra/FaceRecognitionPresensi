<script lang="ts">
  import { onMount, onDestroy } from 'svelte';

  let videoElement: HTMLVideoElement | undefined = $state();
  let canvasElement: HTMLCanvasElement | undefined = $state();
  let stream: MediaStream | null = $state(null);
  
  let isScanning = $state(false);
  let scanInterval: ReturnType<typeof setInterval>;
  let clockInterval: ReturnType<typeof setInterval>;
  
  // State UI Baru
  let currentTime = $state(new Date());
  let recentLogs: { id: string, name: string, nim: string, time: string, similarity: number }[] = $state([]);
  let currentScannedName: string | null = $state(null);
  
  // State untuk Sesi Kelas
  let sessionId = $state('');
  let courseName = $state('Memuat...');
  
  // State untuk Bounding Box & Live Info
  let faceBox = $state({ x1: 0, y1: 0, x2: 0, y2: 0, show: false });
  let liveInfo = $state({ name: '', nim: '', similarity: 0, threshold: 0.75, match: false });

  onMount(async () => {
    // Ambil parameter sesi dari URL
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
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image: frame, session_id: sessionId })
        });
        
        if (response.ok) {
          const data = await response.json();
          
          // 1. Update Bounding Box
          if (data.box) {
            faceBox = { 
              x1: data.box[0], y1: data.box[1], 
              x2: data.box[2], y2: data.box[3], 
              show: true 
            };
          }

          // 2. Update Live Info Label
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

          // 3. Handle Log Presensi (Hanya jika match baru)
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
    }, 1000); // Scan setiap 1 detik
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
    if (confirm("Apakah Anda yakin ingin menutup sesi kelas ini? Mahasiswa yang terlambat tidak akan bisa absen lagi.")) {
      try {
        await fetch(`http://localhost:8000/api/sessions/${sessionId}/close`, {
          method: 'POST'
        });
        
        // Hentikan proses scan dan matikan kamera sebelum pindah halaman
        stopScanning();
        if (stream) {
          stream.getTracks().forEach(t => t.stop());
        }
        
        window.location.href = '/dashboard';
      } catch (err) {
        alert("Gagal menutup sesi.");
      }
    }
  }

  // Hitung posisi kotak wajah relatif terhadap ukuran video container
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

<div class="min-h-screen bg-gray-100 flex flex-col">
  <header class="bg-indigo-900 text-white p-4 shadow-md flex justify-between items-center">
    <div>
      <h1 class="text-2xl font-bold">Presensi: {courseName}</h1>
      <p class="text-indigo-200 text-sm">Gedung Fakultas - Kelas Hari Ini</p>
    </div>
    <div class="text-right">
      <div class="text-3xl font-mono font-bold">
        {currentTime.toLocaleTimeString('id-ID')}
      </div>
    </div>
  </header>

  <main class="flex-1 flex flex-col lg:flex-row p-6 gap-6 h-[calc(100vh-88px)]">
    
    <div class="lg:w-2/3 flex flex-col gap-4">
      <div class="bg-white p-2 rounded-xl shadow-lg border-2 border-gray-200 flex-1 flex flex-col relative overflow-hidden">
        
        <div class="relative flex-1 bg-black rounded-lg overflow-hidden flex items-center justify-center">
          <!-- svelte-ignore a11y_media_has_caption -->
          <video bind:this={videoElement} autoplay playsinline class="w-full h-full object-cover transform scale-x-[-1]"></video>
          
          <!-- DINAMIC BOUNDING BOX -->
          {#if faceBox.show && isScanning}
            <div 
              class="absolute border-4 transition-all duration-200 ease-out flex flex-col items-center {liveInfo.match ? 'border-green-500' : 'border-red-500'}"
              style={getBoxStyle(faceBox)}
            >
              <!-- Label Info Di Atas Kotak -->
              <div class="absolute -top-12 bg-black/80 text-white text-[10px] px-2 py-1 rounded-md whitespace-nowrap flex flex-col items-center">
                 <span class="font-bold {liveInfo.match ? 'text-green-400' : 'text-red-400'}">
                   {liveInfo.match ? 'TERVERIFIKASI' : 'TIDAK DIKENAL'}
                 </span>
                 <span>Sim: {(liveInfo.similarity * 100).toFixed(1)}% / Min: {(liveInfo.threshold * 100).toFixed(0)}%</span>
              </div>

              <!-- Label Nama Di Bawah Kotak -->
              <div class="absolute -bottom-10 bg-indigo-600 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg whitespace-nowrap">
                {liveInfo.name}
              </div>
            </div>
          {/if}

          <!-- Overlay Berhasil -->
          {#if currentScannedName}
            <div class="absolute inset-0 bg-green-500/20 backdrop-blur-[2px] flex items-center justify-center animate-fade-in">
              <div class="bg-white p-8 rounded-3xl shadow-2xl flex flex-col items-center border-4 border-green-500">
                <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                  <svg class="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M5 13l4 4L19 7"></path></svg>
                </div>
                <h3 class="text-2xl font-black text-gray-800 text-center">{currentScannedName}</h3>
                <p class="text-green-600 font-bold mt-2 uppercase tracking-widest">Absensi Tercatat</p>
              </div>
            </div>
          {/if}
        </div>
        <canvas bind:this={canvasElement} class="hidden"></canvas>
      </div>

      <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-200 flex justify-between items-center">
        <button onclick={closeSession} class="px-6 py-2 bg-gray-100 text-red-600 font-bold rounded-lg border border-red-200 hover:bg-red-50 transition-colors">
          Tutup Kelas
        </button>
        <button 
          onclick={toggleScan} 
          class={`px-10 py-3 rounded-lg font-bold text-white shadow-md ${isScanning ? 'bg-red-600' : 'bg-indigo-600'}`}
        >
          {isScanning ? 'Stop Kamera' : 'Mulai Scan Wajah'}
        </button>
      </div>
    </div>

    <div class="lg:w-1/3 bg-white rounded-xl shadow-lg border border-gray-200 flex flex-col overflow-hidden">
      <div class="bg-slate-50 border-b p-4"><h2 class="text-xl font-bold">Log Kehadiran</h2></div>
      <div class="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50/50">
        {#each recentLogs as log (log.id)}
          <li class="bg-white p-3 rounded-lg shadow-sm border border-gray-100 list-none flex justify-between items-center animate-fade-in-down">
            <div>
              <p class="text-sm font-bold text-gray-900">{log.name}</p>
              <p class="text-[10px] text-gray-500">{log.nim}</p>
            </div>
            <div class="text-right">
              <p class="text-xs font-bold">{log.time}</p>
              <p class="text-[9px] text-green-600 font-medium">AI Match: {(log.similarity * 100).toFixed(0)}%</p>
            </div>
          </li>
        {/each}
      </div>
    </div>
  </main>
</div>

<style>
  @keyframes fadeInDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
  .animate-fade-in-down { animation: fadeInDown 0.4s ease-out forwards; }
  @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
  .animate-fade-in { animation: fadeIn 0.3s ease-out; }
</style>
