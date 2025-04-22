<script lang="ts">
	import { superForm } from 'sveltekit-superforms';

	let { data } = $props();

	const { form, errors, message, enhance, tainted } = superForm(data.form, {
		resetForm: false,
		dataType: 'json'
	});
</script>

<div class="container mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
	<div class="mb-6">
		<a href="/admin" class="text-sm text-green-700 hover:text-green-600 hover:underline">
			&larr; Back to Admin Dashboard
		</a>
	</div>

	<h1 class="mb-6 text-3xl font-bold tracking-tight text-gray-900">Manage Tree Inventory</h1>

	{#if $message}
		<div
			class="alert mb-4 shadow-lg"
			class:alert-success={!String($message).toLowerCase().includes('fail') &&
				!String($message).toLowerCase().includes('error')}
			class:alert-error={String($message).toLowerCase().includes('fail') ||
				String($message).toLowerCase().includes('error')}
			role="alert"
		>
			<div>
				{#if String($message).toLowerCase().includes('fail') || String($message)
						.toLowerCase()
						.includes('error')}
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="h-6 w-6 flex-shrink-0 stroke-current"
						fill="none"
						viewBox="0 0 24 24"
						><path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M10 14l2-2m0 0l2-2m-2 2l-2 2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
						/></svg
					>
				{:else}
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
				<span>{$message}</span>
			</div>
		</div>
	{/if}

	{#if $form.trees.length > 0}
		<form method="POST" use:enhance class="space-y-6">
			<div class="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-md">
				<table class="table w-full">
					<thead class="bg-gray-50">
						<tr>
							<th
								class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
							>
								Common Name
							</th>
							<th
								class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
							>
								Scientific Name
							</th>
							<th
								class="w-32 px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
							>
								Inventory
							</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-gray-200">
						{#each $form.trees as tree, index (tree.id)}
							{@const treeErrors = $errors.trees?.[index]}
							<tr>
								<td class="px-6 py-4 text-sm font-medium whitespace-nowrap text-gray-900">
									{tree.common_name}
									<input type="hidden" name="trees[{index}].id" value={tree.id} />
									<input type="hidden" name="trees[{index}].common_name" value={tree.common_name} />
									<input
										type="hidden"
										name="trees[{index}].scientific_name"
										value={tree.scientific_name}
									/>
								</td>
								<td class="px-6 py-4 text-sm whitespace-nowrap text-gray-500 italic">
									{tree.scientific_name}
								</td>
								<td class="px-6 py-4 text-sm whitespace-nowrap text-gray-500">
									<input
										type="number"
										name="trees[{index}].inventory"
										bind:value={$form.trees[index].inventory}
										min="0"
										step="1"
										class="input input-bordered input-sm w-24 {treeErrors?.inventory
											? 'input-error'
											: ''}"
										aria-invalid={!!treeErrors?.inventory}
										aria-describedby={treeErrors?.inventory
											? `inventory-error-${index}`
											: undefined}
									/>
									{#if treeErrors?.inventory}
										<p id="inventory-error-{index}" class="mt-1 text-xs text-red-600">
											{treeErrors.inventory}
										</p>
									{/if}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>

			<div class="flex justify-end pt-4">
				<button type="submit" class="btn btn-primary" disabled={!$tainted}>
					Save Inventory Changes
				</button>
			</div>
		</form>
	{:else}
		<div class="rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
			<p class="text-sm text-gray-500">Could not load tree inventory data.</p>
		</div>
	{/if}
</div>
