<script lang="ts">
  import { onMount, onDestroy } from 'svelte';

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
        const response = await fetch('http://localhost:8000/api/validate', {
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
      const response = await fetch('http://localhost:8000/api/enroll', {
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

<div class="max-w-4xl mx-auto py-10 px-4">
  <div class="mb-8 flex items-center justify-between">
    <h1 class="text-3xl font-bold text-gray-900">Enrollment Biometrik</h1>
    <a href="/" class="text-indigo-600 hover:text-indigo-800 font-medium">&larr; Kembali</a>
  </div>
  
  <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
    <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
      <h2 class="text-xl font-semibold mb-4">Data Mahasiswa</h2>
      <div class="space-y-4">
        <div>
          <label for="nim" class="block text-sm font-medium text-gray-700">NIM</label>
          <input type="text" id="nim" bind:value={nim} disabled={isEnrolling} class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" />
        </div>
        <div>
          <label for="name" class="block text-sm font-medium text-gray-700">Nama Lengkap</label>
          <input type="text" id="name" bind:value={name} disabled={isEnrolling} class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" />
        </div>
        <div class="pt-4">
          <button 
            onclick={startEnrollment} 
            disabled={isEnrolling || !nim || !name}
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {isEnrolling ? 'Proses Validasi Berjalan...' : 'Mulai Pendaftaran Wajah'}
          </button>
        </div>
      </div>
    </div>
    
    <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200 flex flex-col items-center">
      <div class="relative w-full aspect-[3/4] bg-gray-900 rounded-2xl overflow-hidden mb-4 shadow-inner max-w-sm">
        <!-- svelte-ignore a11y_media_has_caption -->
        <video bind:this={videoElement} autoplay playsinline class="absolute inset-0 w-full h-full object-cover transform scale-x-[-1]"></video>
        
        <!-- Masking Overlay ala Face ID -->
        <div class="absolute inset-0 pointer-events-none flex flex-col items-center justify-center">
          <div class="w-[80%] aspect-[3/4] rounded-[50%] border-4 transition-colors duration-300 {isEnrolling ? (isPoseValid ? 'border-green-400 bg-green-400/20' : 'border-yellow-400 bg-transparent') : 'border-gray-400 bg-transparent'} shadow-[0_0_0_9999px_rgba(0,0,0,0.6)]"></div>
        </div>

        {#if isEnrolling && currentInstructionIndex < poses.length}
          <!-- Indikator Progress -->
          <div class="absolute top-4 left-0 right-0 flex justify-center gap-2">
            {#each poses as _, i}
              <div class="w-3 h-3 rounded-full {i < currentInstructionIndex ? 'bg-green-500' : (i === currentInstructionIndex ? 'bg-yellow-400 animate-pulse' : 'bg-gray-500')}"></div>
            {/each}
          </div>
        {/if}
      </div>
      
      <canvas bind:this={canvasElement} class="hidden"></canvas>
      
      <div class="w-full text-center p-4 rounded-md border min-h-[5rem] flex items-center justify-center transition-colors {isPoseValid ? 'bg-green-50 border-green-200' : 'bg-indigo-50 border-indigo-100'}">
        {#if isEnrolling}
          <p class="text-lg font-bold transition-opacity duration-300 {isPoseValid ? 'text-green-700' : 'text-indigo-800'}">
            {feedbackMessage}
          </p>
        {:else}
          <p class="text-sm text-gray-500">
            Posisikan wajah Anda di dalam oval. Ikuti instruksi arah putaran kepala.
          </p>
        {/if}
      </div>
    </div>
  </div>
</div>
