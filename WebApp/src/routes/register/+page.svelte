<script lang="ts">
	// Ensure correct import path for client-side superForm
	import { superForm } from 'sveltekit-superforms/client';
	import type { ActionResult } from '@sveltejs/kit';
	import { goto } from '$app/navigation';
	import { applyAction } from '$app/forms';
	// import SuperDebug from 'sveltekit-superforms/client/SuperDebug.svelte'; // Optional for debugging

	let { data } = $props();

	// Client API:
	const { form, errors, message, enhance } = superForm(data.form);
</script>

<div class="container mx-auto max-w-md px-6 py-12">
	<h1 class="mb-6 text-center text-3xl font-bold text-gray-800">Register</h1>
	<p class="mb-6 text-center text-gray-600">
		Already have an account? <a href="/login" class="text-green-700 underline hover:text-green-600"
			>Login here</a
		>
	</p>

	<!-- Display general form messages (like success/failure) -->
	{#if $message}
		<!-- Apply styling based on message type if available, otherwise default to info/success -->
		<div
			class="mb-4 rounded border p-3 {$message?.type === 'error'
				? 'border-red-400 bg-red-100 text-red-700'
				: 'border-green-400 bg-green-100 text-green-700'}"
			role="alert"
		>
			{$message.text ?? $message}
			<!-- Display message text or the message itself -->
		</div>
	{/if}

	<form method="POST" use:enhance class="space-y-6">
		<!-- First and Last Name -->
		<div class="flex space-x-4">
			<div class="flex-1">
				<label for="firstName" class="mb-2 block text-sm font-medium text-gray-700"
					>First Name</label
				>
				<input
					type="text"
					id="firstName"
					name="firstName"
					placeholder="Alvaro"
					class="input input-bordered w-full {$errors.firstName ? 'input-error' : ''}"
					bind:value={$form.firstName}
					aria-invalid={$errors.firstName ? 'true' : undefined}
					aria-describedby={$errors.firstName ? 'firstName-error' : undefined}
				/>
				{#if $errors.firstName}
					<p id="firstName-error" class="mt-1 text-sm text-red-600">{$errors.firstName}</p>
				{/if}
			</div>
			<div class="flex-1">
				<label for="lastName" class="mb-2 block text-sm font-medium text-gray-700">Last Name</label>
				<input
					type="text"
					id="lastName"
					name="lastName"
					placeholder="Monge"
					class="input input-bordered w-full {$errors.lastName ? 'input-error' : ''}"
					bind:value={$form.lastName}
					aria-invalid={$errors.lastName ? 'true' : undefined}
					aria-describedby={$errors.lastName ? 'lastName-error' : undefined}
				/>
				{#if $errors.lastName}
					<p id="lastName-error" class="mt-1 text-sm text-red-600">{$errors.lastName}</p>
				{/if}
			</div>
		</div>

		<!-- Email Input -->
		<div>
			<label for="email" class="mb-2 block text-sm font-medium text-gray-700">Email</label>
			<input
				type="email"
				id="email"
				name="email"
				placeholder="alex.garcia@example.com"
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
				placeholder="•••••••• (min. 8 characters)"
				class="input input-bordered w-full {$errors.password ? 'input-error' : ''}"
				bind:value={$form.password}
				aria-invalid={$errors.password ? 'true' : undefined}
				aria-describedby={$errors.password ? 'password-error' : undefined}
			/>
			{#if $errors.password}
				<p id="password-error" class="mt-1 text-sm text-red-600">{$errors.password}</p>
			{/if}
		</div>

		<!-- Street Address Input -->
		<div>
			<label for="street" class="mb-2 block text-sm font-medium text-gray-700">Street Address</label
			>
			<input
				type="text"
				id="street"
				name="street"
				placeholder="1234 Oak St"
				class="input input-bordered w-full {$errors.street ? 'input-error' : ''}"
				bind:value={$form.street}
				aria-invalid={$errors.street ? 'true' : undefined}
				aria-describedby={$errors.street ? 'street-error' : undefined}
			/>
			{#if $errors.street}
				<p id="street-error" class="mt-1 text-sm text-red-600">{$errors.street}</p>
			{/if}
		</div>

		<!-- Zip Code and Neighborhood -->
		<div class="flex space-x-4">
			<div class="flex-1">
				<label for="zipCode" class="mb-2 block text-sm font-medium text-gray-700">ZIP Code</label>
				<input
					type="text"
					id="zipCode"
					name="zipCode"
					placeholder="94607"
					class="input input-bordered w-full {$errors.zipCode ? 'input-error' : ''}"
					bind:value={$form.zipCode}
					aria-invalid={$errors.zipCode ? 'true' : undefined}
					aria-describedby={$errors.zipCode ? 'zipCode-error' : undefined}
				/>
				{#if $errors.zipCode}
					<p id="zipCode-error" class="mt-1 text-sm text-red-600">{$errors.zipCode}</p>
				{/if}
			</div>
			<!-- Neighborhood Dropdown -->
			<div>
				<label for="neighborhood" class="mb-2 block text-sm font-medium text-gray-700"
					>Neighborhood</label
				>
				<select
					id="neighborhood"
					name="neighborhood"
					class="select select-bordered w-full {$errors.neighborhood ? 'select-error' : ''}"
					bind:value={$form.neighborhood}
					aria-invalid={$errors.neighborhood ? 'true' : undefined}
					aria-describedby={$errors.neighborhood ? 'treeId-error' : undefined}
				>
					<option disabled selected value={undefined}>Choose a neighborhood</option>
					{#each data.neighborhoods as neighborhood}
						<option value={neighborhood}>
							{neighborhood}
						</option>
					{/each}
				</select>
				{#if $errors.neighborhood}
					<p id="neighborhood-error" class="mt-1 text-sm text-red-600">{$errors.neighborhood}</p>
				{/if}
				{#if data.neighborhoods.length === 0}
					<p class="mt-1 text-sm text-yellow-600">Could not load available neighborhoods.</p>
				{/if}
			</div>
		</div>

		<!-- Submit Button -->
		<button type="submit" class="btn btn-primary w-full bg-green-700 text-white hover:bg-green-600">
			Register
		</button>
	</form>

	<!-- <SuperDebug data={{ $form, $errors, $message }} /> -->
	<!-- Uncomment for debugging -->
</div>
