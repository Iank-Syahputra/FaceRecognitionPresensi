<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { API_BASE_URL } from '$lib/api';

  // Svelte 5: Variabel yang mengubah UI harus dibungkus dengan $state()
  let videoElement: HTMLVideoElement | undefined = $state();
  let canvasElement: HTMLCanvasElement | undefined = $state();
  let stream: MediaStream | null = $state(null);
  
  let nim = $state('');
  let name = $state('');
  let isEnrolling = $state(false);
  let currentInstructionIndex = $state(0);
  let feedbackMessage = $state('');
  let isPoseValid = $state(false);
  
  // Ganti Interval dengan penanda status berjalan (untuk async loop)
  let isValidationRunning = false;
  
  const poses = [
    { id: "depan", text: "Tatap lurus ke depan" },
    { id: "kanan", text: "Tolehkan kepala sedikit ke KANAN" },
    { id: "kiri", text: "Tolehkan kepala sedikit ke KIRI" },
    { id: "bawah", text: "Tundukkan kepala sedikit ke BAWAH" }
  ];
  
  let capturedFrames: string[] = $state([]);

  onMount(async () => {
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoElement) {
        videoElement.srcObject = stream;
      }
    } catch (err) {
      console.error("Error accessing camera:", err);
      alert("Tidak dapat mengakses kamera. Pastikan izin telah diberikan.");
    }
  });

  onDestroy(() => {
    isValidationRunning = false;
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }
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

  function startEnrollment() {
    if (!nim || !name) {
      alert("Mohon isi NIM dan Nama terlebih dahulu.");
      return;
    }
    
    isEnrolling = true;
    currentInstructionIndex = 0;
    capturedFrames = [];
    isPoseValid = false;
    isValidationRunning = true;
    
    // Mulai loop rekursif
    validationLoop();
  }
  
  // Fungsi loop sekuensial (async)
  async function validationLoop() {
    if (!isValidationRunning || currentInstructionIndex >= poses.length) return;
    
    feedbackMessage = poses[currentInstructionIndex].text;
    const expectedPose = poses[currentInstructionIndex].id;
    const frame = captureFrame();

    if (frame) {
      try {
        const response = await fetch(`${API_BASE_URL}/api/validate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image: frame, expected_pose: expectedPose })
        });
        
        if (response.ok && isValidationRunning) { // Cek lagi apakah proses belum dibatalkan
          const result = await response.json();
          feedbackMessage = result.message;
          isPoseValid = result.valid;

          if (result.valid) {
            // Jeda sejenak sistem validasi
            capturedFrames.push(frame);
            
            // Tunggu 1 detik agar UI hijau sempat terlihat
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            currentInstructionIndex++;
            if (currentInstructionIndex < poses.length) {
              isPoseValid = false;
              // Lanjut ke pose berikutnya tanpa delay
              validationLoop();
              return; 
            } else {
              isValidationRunning = false;
              finishEnrollment();
              return;
            }
          }
        }
      } catch (err) {
        console.error("Validation error:", err);
      }
    }
    
    // Jika belum valid, ulangi lagi setelah 500ms
    if (isValidationRunning) {
      setTimeout(validationLoop, 500);
    }
  }

  async function finishEnrollment() {
    feedbackMessage = "Memproses dan menyimpan data biometrik...";
    try {
      const response = await fetch(`${API_BASE_URL}/api/enroll`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nim, name, frames: capturedFrames })
      });
      
      if (response.ok) {
        alert("Enrollment berhasil!");
        nim = '';
        name = '';
      } else {
        const error = await response.json();
        alert("Gagal: " + (error.detail || "Terjadi kesalahan"));
      }
    } catch (err) {
      alert("Gagal terhubung ke server.");
    } finally {
      isEnrolling = false;
      isValidationRunning = false;
      currentInstructionIndex = 0;
      capturedFrames = [];
      feedbackMessage = '';
      isPoseValid = false;
    }
  }
</script>

<div class="min-h-screen bg-campus-surface pb-10">
  
  <!-- Header -->
  <header class="bg-campus-navy text-white px-4 py-4 sm:px-6 shadow-md flex items-center justify-between sticky top-0 z-10">
    <div class="flex items-center gap-3">
      <a href="/" class="p-2 bg-white/10 rounded-full hover:bg-white/20 transition-colors">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
      </a>
      <h1 class="text-xl font-bold tracking-tight">Registrasi Wajah Baru</h1>
    </div>
  </header>

  <div class="max-w-4xl mx-auto mt-6 px-4">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8 items-start">
      
      <!-- Kolom Kamera (Diubah urutannya di mobile agar muncul duluan) -->
      <div class="bg-white p-4 sm:p-6 rounded-3xl shadow-xl border border-white flex flex-col items-center order-1 lg:order-2">
        <div class="relative w-full max-w-sm aspect-[3/4] bg-campus-navy rounded-3xl overflow-hidden mb-5 shadow-inner">
          <!-- svelte-ignore a11y_media_has_caption -->
          <video bind:this={videoElement} autoplay playsinline class="absolute inset-0 w-full h-full object-cover transform scale-x-[-1]"></video>
          
          <!-- Masking Overlay ala Face ID -->
          <div class="absolute inset-0 pointer-events-none flex flex-col items-center justify-center">
            <div class="w-[75%] aspect-[3/4] rounded-[50%] border-4 transition-colors duration-300 {isEnrolling ? (isPoseValid ? 'border-emerald-400 bg-emerald-400/20' : 'border-yellow-400 bg-transparent') : 'border-white/50 bg-transparent'} shadow-[0_0_0_9999px_rgba(1,16,37,0.7)]"></div>
          </div>

          {#if isEnrolling && currentInstructionIndex < poses.length}
            <!-- Indikator Progress -->
            <div class="absolute top-6 left-0 right-0 flex justify-center gap-3">
              {#each poses as _, i}
                <div class="w-3 h-3 rounded-full shadow-sm {i < currentInstructionIndex ? 'bg-emerald-500 scale-100' : (i === currentInstructionIndex ? 'bg-yellow-400 animate-pulse scale-125' : 'bg-white/30 scale-75')} transition-transform"></div>
              {/each}
            </div>
          {/if}
        </div>
        
        <canvas bind:this={canvasElement} class="hidden"></canvas>
        
        <div class="w-full text-center p-4 rounded-2xl border min-h-[5rem] flex items-center justify-center transition-colors {isEnrolling ? (isPoseValid ? 'bg-emerald-50 border-emerald-200' : 'bg-yellow-50 border-yellow-200') : 'bg-campus-surface/50 border-campus-secondary/20'}">
          {#if isEnrolling}
            <p class="text-base sm:text-lg font-bold transition-opacity duration-300 {isPoseValid ? 'text-emerald-700' : 'text-yellow-700'}">
              {feedbackMessage}
            </p>
          {:else}
            <p class="text-sm font-medium text-campus-secondary">
              Posisikan wajah di dalam oval. Ikuti instruksi arah putaran kepala.
            </p>
          {/if}
        </div>
      </div>

      <!-- Kolom Form Data -->
      <div class="bg-white p-6 rounded-3xl shadow-xl border border-white order-2 lg:order-1">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 bg-campus-surface text-campus-primary rounded-xl flex items-center justify-center">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2"></path></svg>
          </div>
          <h2 class="text-xl font-bold text-campus-navy">Data Identitas</h2>
        </div>

        <div class="space-y-5">
          <div>
            <label for="nim" class="block text-sm font-bold text-campus-secondary uppercase tracking-wider mb-1.5">Nomor Induk Mahasiswa</label>
            <input type="text" id="nim" bind:value={nim} disabled={isEnrolling} placeholder="Masukkan NIM..." class="block w-full border-2 border-campus-muted/30 rounded-xl bg-campus-surface/20 py-3 px-4 focus:outline-none focus:border-campus-primary focus:ring-2 focus:ring-campus-primary/20 transition-colors sm:text-base font-mono font-medium disabled:opacity-50" />
          </div>
          <div>
            <label for="name" class="block text-sm font-bold text-campus-secondary uppercase tracking-wider mb-1.5">Nama Lengkap</label>
            <input type="text" id="name" bind:value={name} disabled={isEnrolling} placeholder="Nama sesuai KTP..." class="block w-full border-2 border-campus-muted/30 rounded-xl bg-campus-surface/20 py-3 px-4 focus:outline-none focus:border-campus-primary focus:ring-2 focus:ring-campus-primary/20 transition-colors sm:text-base font-medium disabled:opacity-50" />
          </div>
          
          <div class="pt-6 border-t border-campus-muted/20">
            <button 
              onclick={startEnrollment} 
              disabled={isEnrolling || !nim || !name}
              class="w-full flex justify-center py-3.5 px-4 border border-transparent rounded-xl shadow-lg shadow-campus-primary/30 text-base font-bold text-white bg-campus-primary hover:bg-campus-navy focus:outline-none focus:ring-4 focus:ring-campus-primary/50 transition-all duration-300 disabled:bg-campus-muted disabled:shadow-none disabled:cursor-not-allowed transform active:scale-[0.98]"
            >
              {isEnrolling ? 'Validasi Sedang Berjalan...' : 'Mulai Pendaftaran Wajah'}
            </button>
          </div>
        </div>
      </div>

    </div>
  </div>
</div>