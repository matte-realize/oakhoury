<script lang="ts">
	import { superForm } from 'sveltekit-superforms/client';
	// import SuperDebug from 'sveltekit-superforms/client/SuperDebug.svelte'; // Optional

	let { data } = $props();

	const { form, errors, message, enhance } = superForm(data.form);
</script>

<div class="container mx-auto max-w-2xl px-4 py-12 sm:px-6 lg:px-8">
	<div class="mb-6">
		<a href="/dashboard" class="text-sm text-green-700 hover:text-green-600 hover:underline">
			&larr; Back to Dashboard
		</a>
	</div>

	<div class="overflow-hidden rounded-lg bg-white shadow">
		<div class="border-b border-gray-200 bg-white px-4 py-5 sm:px-6">
			<h1 class="text-xl leading-6 font-semibold text-gray-900">Request a New Tree</h1>
			<p class="mt-1 max-w-2xl text-sm text-gray-500">
				Fill out the details below to request a tree for your property.
			</p>
		</div>

		<form method="POST" use:enhance class="space-y-6 p-4 sm:p-6">
			<!-- Display general form messages -->
			{#if $message}
				<div class="rounded border border-red-400 bg-red-100 p-3 text-red-700" role="alert">
					{$message}
				</div>
			{/if}

			<!-- Tree Selection Dropdown -->
			<div>
				<label for="treeId" class="mb-2 block text-sm font-medium text-gray-700"
					>Select Tree Type</label
				>
				<select
					id="treeId"
					name="treeId"
					class="select select-bordered w-full {$errors.treeId ? 'select-error' : ''}"
					bind:value={$form.treeId}
					aria-invalid={$errors.treeId ? 'true' : undefined}
					aria-describedby={$errors.treeId ? 'treeId-error' : undefined}
				>
					<option disabled selected value={undefined}>Choose a tree</option>
					{#each data.availableTrees as tree}
						<option value={tree.id}>
							{tree.commonName} ({tree.scientificName})
						</option>
					{/each}
				</select>
				{#if $errors.treeId}
					<p id="treeId-error" class="mt-1 text-sm text-red-600">{$errors.treeId}</p>
				{/if}
				{#if data.availableTrees.length === 0}
					<p class="mt-1 text-sm text-yellow-600">Could not load available tree types.</p>
				{/if}
			</div>

			<!-- Site Description Textarea -->
			<div>
				<label for="siteDescription" class="mb-2 block text-sm font-medium text-gray-700"
					>Site Description</label
				>
				<textarea
					id="siteDescription"
					name="siteDescription"
					rows="4"
					placeholder="Describe where you'd like the tree planted (e.g., 'Front yard, near the sidewalk', 'Backyard, sunny spot away from power lines'). Max 500 characters."
					class="textarea textarea-bordered w-full {$errors.siteDescription
						? 'textarea-error'
						: ''}"
					bind:value={$form.siteDescription}
					aria-invalid={$errors.siteDescription ? 'true' : undefined}
					aria-describedby={$errors.siteDescription ? 'siteDescription-error' : undefined}
				></textarea>
				{#if $errors.siteDescription}
					<p id="siteDescription-error" class="mt-1 text-sm text-red-600">
						{$errors.siteDescription}
					</p>
				{/if}
			</div>

			<!-- Address Confirmation -->
			<div class="rounded-md border border-gray-200 bg-gray-50 p-4">
				<h3 class="mb-2 text-sm font-medium text-gray-600">Planting Address (from your profile)</h3>
				<p class="text-sm text-gray-800">{data.user.street}</p>
				<p class="text-sm text-gray-800">
					{data.user.neighborhood}, Oakland, CA {data.user.zipCode}
				</p>
				<p class="mt-2 text-xs text-gray-500">
					If this address is incorrect, please send us an email and we will change you address on
					file.
					<br />
					oakhourytrees@gmail.com
				</p>
			</div>

			<!-- Submit Button -->
			<div class="flex justify-end">
				<button type="submit" class="btn btn-primary bg-green-700 text-white hover:bg-green-600">
					Submit Request
				</button>
			</div>
		</form>
	</div>
	<!-- <SuperDebug data={{ $form, $errors, $message }} /> -->
</div>
