<script lang="ts">
	import { superForm } from 'sveltekit-superforms/client';

	const { data } = $props();

	// Client API:
	const { form, errors, message, enhance } = superForm(data.form);
</script>

<div class="container mx-auto max-w-md px-6 py-12">
	<h1 class="mb-6 text-center text-3xl font-bold text-gray-800">Login</h1>
	<p class="mb-6 text-center text-gray-600">
		Don't have an account? <a
			href="/register"
			class="text-green-700 underline hover:text-green-600"
		>
			Register here
		</a>
	</p>
	{#if $message}<h3 class="text-sm font-bold text-red-500">{$message}</h3>{/if}

	<form method="POST" use:enhance class="space-y-6">
		<!-- Email Input -->
		<div>
			<label for="email" class="mb-2 block text-sm font-medium text-gray-700">Email</label>
			<input
				type="email"
				id="email"
				name="email"
				placeholder="you@example.com"
				class="input input-bordered w-full {$errors.email ? 'input-error' : ''}"
				bind:value={$form.email}
				aria-invalid={$errors.email ? 'true' : undefined}
				aria-describedby={$errors.email ? 'email-error' : undefined}
			/>
			{#if $errors.email}
				<p id="email-error" class="mt-1 text-sm text-red-600">{$errors.email}</p>
			{/if}
		</div>

		<!-- Password Input -->
		<div>
			<label for="password" class="mb-2 block text-sm font-medium text-gray-700">Password</label>
			<input
				type="password"
				id="password"
				name="password"
				placeholder="••••••••"
				class="input input-bordered w-full {$errors.password ? 'input-error' : ''}"
				bind:value={$form.password}
				aria-invalid={$errors.password ? 'true' : undefined}
				aria-describedby={$errors.password ? 'password-error' : undefined}
			/>
			{#if $errors.password}
				<p id="password-error" class="mt-1 text-sm text-red-600">{$errors.password}</p>
			{/if}
		</div>

		<!-- Submit Button -->
		<button type="submit" class="btn btn-primary w-full bg-green-700 text-white hover:bg-green-600">
			Login
		</button>
	</form>
</div>
