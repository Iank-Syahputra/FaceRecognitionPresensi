<script lang="ts">
  import { onMount } from 'svelte';
  import { clearAuth, saveAuth } from '$lib/auth';

  let email = $state('');
  let password = $state('');
  let name = $state('');
  let role = $state('student');
  let isRegister = $state(false);
  let loading = $state(false);
  let message = $state('');

  function resetForm() {
    email = '';
    password = '';
    name = '';
    role = 'student';
    message = '';
  }

  onMount(() => {
    clearAuth();
  });

  async function submit() {
    loading = true;
    message = '';
    const endpoint = isRegister ? '/api/auth/register' : '/api/auth/login';
    const payload = isRegister
      ? { email, password, name, role }
      : { email, password };

    try {
      const response = await fetch('http://localhost:8000' + endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const result = await response.json();
      if (!response.ok) {
        message = result.detail || result.message || 'Gagal masuk. Periksa kembali data Anda.';
        return;
      }

      saveAuth(result.user, result.access_token);
      window.location.href = '/dashboard';
    } catch (err) {
      message = 'Gagal terhubung ke server. Coba lagi nanti.';
    } finally {
      loading = false;
    }
  }
</script>

<div class="min-h-screen bg-campus-surface flex items-center justify-center py-12 px-4 sm:px-6">
  <div class="w-full max-w-xl bg-white rounded-3xl shadow-2xl border border-white overflow-hidden">
    <div class="bg-campus-navy text-white p-8 sm:p-10">
      <h1 class="text-3xl font-black">{isRegister ? 'Daftar Akun' : 'Masuk'}</h1>
      <p class="mt-3 text-campus-surface/80 text-sm leading-relaxed">
        {isRegister ? 'Buat akun mahasiswa atau dosen untuk mengakses dashboard.' : 'Masuk untuk melanjutkan ke dashboard dan fitur presensi.'}
      </p>
    </div>

    <div class="p-8 sm:p-10 space-y-6">
      {#if message}
        <div class="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          {message}
        </div>
      {/if}

      <div class="grid gap-6">
        <div>
          <label class="block text-xs font-bold uppercase tracking-widest mb-2 text-campus-secondary">Email</label>
          <input type="email" bind:value={email} placeholder="contoh@kampus.ac.id" class="w-full rounded-2xl border border-campus-muted/30 bg-campus-surface/60 px-4 py-3 focus:outline-none focus:border-campus-primary" />
        </div>

        {#if isRegister}
          <div>
            <label class="block text-xs font-bold uppercase tracking-widest mb-2 text-campus-secondary">Nama Lengkap</label>
            <input type="text" bind:value={name} placeholder="Nama lengkap Anda" class="w-full rounded-2xl border border-campus-muted/30 bg-campus-surface/60 px-4 py-3 focus:outline-none focus:border-campus-primary" />
          </div>
        {/if}

        <div>
          <label class="block text-xs font-bold uppercase tracking-widest mb-2 text-campus-secondary">Password</label>
          <input type="password" bind:value={password} placeholder="Minimal 8 karakter" class="w-full rounded-2xl border border-campus-muted/30 bg-campus-surface/60 px-4 py-3 focus:outline-none focus:border-campus-primary" />
        </div>

        {#if isRegister}
          <div>
            <label class="block text-xs font-bold uppercase tracking-widest mb-2 text-campus-secondary">Role</label>
            <select bind:value={role} class="w-full rounded-2xl border border-campus-muted/30 bg-campus-surface/60 px-4 py-3 focus:outline-none focus:border-campus-primary">
              <option value="student">Mahasiswa</option>
              <option value="professor">Dosen</option>
            </select>
          </div>
        {/if}
      </div>

      <button onclick={submit} disabled={loading || !email || !password || (isRegister && !name)} class="w-full rounded-2xl bg-campus-primary text-white py-3.5 font-bold hover:bg-campus-navy transition-all disabled:opacity-60">
        {loading ? 'Memproses...' : isRegister ? 'Buat Akun' : 'Masuk'}
      </button>

      <button onclick={() => { isRegister = !isRegister; message = ''; }} class="w-full rounded-2xl border border-campus-muted/30 bg-campus-surface/70 text-campus-navy py-3.5 font-bold hover:border-campus-primary transition-all">
        {isRegister ? 'Sudah punya akun? Masuk' : 'Belum punya akun? Daftar'}
      </button>
    </div>
  </div>
</div>
