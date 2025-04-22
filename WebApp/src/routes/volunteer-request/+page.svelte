<script lang="ts">
	import { superForm } from 'sveltekit-superforms/client';

	const { data } = $props();

	const { form, errors, message, enhance } = superForm(data.form, {
		resetForm: true
	});
</script>

<div class="container mx-auto max-w-4xl px-6 py-12">
	<a href="/dashboard" class="btn btn-ghost"> &larr; Back</a>
	<h1 class="mb-6 text-center text-3xl font-bold text-gray-800">Become a Volunteer!</h1>
	<p class="mb-6 text-center text-gray-600">
		Help grow Oakland's urban canopy! Our volunteers are crucial for planting events, site
		assessments, and community outreach. No experience necessary, just a willingness to help make
		Oakland greener.
	</p>
	<p class="mb-8 text-center text-gray-600">
		Submit this form to express your interest. Feel free to add any notes about your availability,
		specific interests (planting, outreach, etc.), or questions you might have.
	</p>

	{#if $message}
		<div class="mb-4 rounded border border-green-400 bg-green-100 p-6 text-green-700" role="alert">
			<span class="block sm:inline">{$message}</span>
		</div>
	{/if}

	<form method="POST" use:enhance class="space-y-6">
		<!-- Notes Textarea -->
		<div>
			<label for="notes" class="mb-2 block text-sm font-medium text-gray-700"
				>Notes (Optional)</label
			>
			<textarea
				id="notes"
				name="notes"
				rows="4"
				placeholder="Let us know your availability, interests, or any questions..."
				class="textarea textarea-bordered w-full {$errors.notes ? 'textarea-error' : ''}"
				bind:value={$form.notes}
				aria-invalid={$errors.notes ? 'true' : undefined}
				aria-describedby={$errors.notes ? 'notes-error' : undefined}
			></textarea>
			{#if $errors.notes}
				<p id="notes-error" class="mt-1 text-sm text-red-600">{$errors.notes}</p>
			{/if}
		</div>

		<!-- Submit Button -->
		<button type="submit" class="btn btn-primary w-full bg-green-700 text-white hover:bg-green-600">
			Submit Volunteer Interest
		</button>
	</form>
</div>
