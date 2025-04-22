<script lang="ts">
	import { page } from '$app/stores';
	import { superForm } from 'sveltekit-superforms';

	let { data } = $props();
	const { treeRequestId } = $page.params;

	const form = superForm(data.form);

	const { form: formData, enhance, message, errors } = form;

	// Helper to format date for datetime-local input (YYYY-MM-DDTHH:mm)
	function getLocalDateTimeString(date = new Date()) {
		const year = date.getFullYear();
		const month = (date.getMonth() + 1).toString().padStart(2, '0');
		const day = date.getDate().toString().padStart(2, '0');
		const hours = date.getHours().toString().padStart(2, '0');
		const minutes = date.getMinutes().toString().padStart(2, '0');
		return `${year}-${month}-${day}T${hours}:${minutes}`;
	}

	$formData.event_timestamp = getLocalDateTimeString();
</script>

<div class="container mx-auto max-w-xl px-4 py-12 sm:px-6 lg:px-8">
	<div class="mb-6">
		<a
			href="/admin/details/{treeRequestId}"
			class="text-sm text-green-700 hover:text-green-600 hover:underline"
		>
			&larr; Back to Request Details
		</a>
	</div>
	<h1 class="mb-6 text-2xl font-bold tracking-tight text-gray-900">
		Schedule Planting for Request ID: {treeRequestId}
	</h1>

	{#if $message}
		<div
			class="alert mb-4 shadow-lg"
			class:alert-success={$message?.type === 'success'}
			class:alert-error={$message?.type === 'error'}
		>
			<div>
				{#if $message?.type === 'success'}
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="h-6 w-6 flex-shrink-0 stroke-current"
						fill="none"
						viewBox="0 0 24 24"
						><path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
						/></svg
					>
				{/if}
				{#if $message?.type === 'error'}
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="h-6 w-6 flex-shrink-0 stroke-current"
						fill="none"
						viewBox="0 0 24 24"
						><path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
						/></svg
					>
				{/if}
				<span>{$message.text}</span>
			</div>
		</div>
	{/if}

	<form method="POST" use:enhance class="space-y-6 rounded-lg bg-white p-8 shadow-md">
		<div>
			<label for="event_timestamp" class="block text-sm font-medium text-gray-700">
				Date and Time
			</label>
			<input
				type="datetime-local"
				id="event_timestamp"
				name="event_timestamp"
				bind:value={$formData.event_timestamp}
				class="input input-bordered mt-1 block w-full"
				aria-invalid={$errors.event_timestamp ? 'true' : undefined}
			/>
			{#if $errors.event_timestamp}
				<p class="mt-2 text-sm text-red-600">{$errors.event_timestamp}</p>
			{/if}
		</div>

		<div>
			<label for="notes" class="block text-sm font-medium text-gray-700"> Notes (Optional) </label>
			<textarea
				id="notes"
				name="notes"
				bind:value={$formData.notes}
				rows="4"
				class="textarea textarea-bordered mt-1 block w-full"
				aria-invalid={$errors.notes ? 'true' : undefined}
			></textarea>
			{#if $errors.notes}
				<p class="mt-2 text-sm text-red-600">{$errors.notes}</p>
			{/if}
		</div>

		<div>
			<button type="submit" class="btn btn-secondary w-full"> Schedule Planting </button>
		</div>
	</form>
</div>
