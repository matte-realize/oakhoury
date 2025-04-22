<script lang="ts">
	import { page } from '$app/state';
	import { superForm } from 'sveltekit-superforms';

	let { data } = $props();
	const visitEventId = page.params.visitEventId;
	const treeRequestId = data.treeRequestId || 'N/A';

	const form = superForm(data.form, { dataType: 'json' });

	const { form: formData, enhance, message, errors } = form;
</script>

<div class="container mx-auto max-w-xl px-4 py-12 sm:px-6 lg:px-8">
	<div class="mb-6">
		{#if treeRequestId !== 'N/A'}
			<a
				href="/admin/details/{treeRequestId}"
				class="text-sm text-green-700 hover:text-green-600 hover:underline"
			>
				&larr; Back to Request Details (ID: {treeRequestId})
			</a>
		{:else}
			<a href="/admin" class="text-sm text-green-700 hover:text-green-600 hover:underline">
				&larr; Back to Admin Dashboard
			</a>
		{/if}
	</div>
	<h1 class="mb-6 text-2xl font-bold tracking-tight text-gray-900">
		Record Outcome for Visit ID: {visitEventId}
	</h1>

	{#if $message}
		<div class="alert mb-4 shadow-lg">
			<span>{$message}</span>
		</div>
	{/if}

	<form method="POST" use:enhance class="space-y-6 rounded-lg bg-white p-8 shadow-md">
		<!-- Observations Textarea -->
		<div>
			<label for="observations" class="block text-sm font-medium text-gray-700">
				Observations / Notes
			</label>
			<textarea
				id="observations"
				name="observations"
				bind:value={$formData.observations}
				rows="6"
				class="textarea textarea-bordered mt-1 block w-full {$errors.observations
					? 'textarea-error'
					: ''}"
				placeholder="Enter details about the site visit, resident interaction, site conditions, etc."
				aria-invalid={$errors.observations ? 'true' : undefined}
			></textarea>
			{#if $errors.observations}
				<p class="mt-2 text-sm text-red-600">{$errors.observations}</p>
			{/if}
		</div>

		<!-- Photo Library Link Input -->
		<div>
			<label for="photo_library_link" class="block text-sm font-medium text-gray-700">
				Photo Library Link (Optional)
			</label>
			<input
				type="url"
				id="photo_library_link"
				name="photo_library_link"
				bind:value={$formData.photo_library_link}
				class="input input-bordered mt-1 block w-full {$errors.photo_library_link
					? 'input-error'
					: ''}"
				placeholder="https://photos.example.com/..."
				aria-invalid={$errors.photo_library_link ? 'true' : undefined}
			/>
			{#if $errors.photo_library_link}
				<p class="mt-2 text-sm text-red-600">{$errors.photo_library_link}</p>
			{/if}
		</div>

		<!-- Additional Visit Required Checkbox -->
		<div class="form-control">
			<label class="label cursor-pointer justify-start gap-4">
				<input
					type="checkbox"
					name="additional_visit_required"
					bind:checked={$formData.additional_visit_required}
					class="checkbox checkbox-primary"
				/>
				<span class="label-text">Additional Visit Required?</span>
			</label>
			{#if $errors.additional_visit_required}
				<p class="mt-1 text-sm text-red-600">{$errors.additional_visit_required}</p>
			{/if}
		</div>

		<!-- Submit Button -->
		<div>
			<button type="submit" class="btn btn-primary w-full"> Record Visit Outcome </button>
		</div>
	</form>
</div>
