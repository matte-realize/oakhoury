<script lang="ts">
	import { superForm } from 'sveltekit-superforms';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const { queryTasks, neighborhoods, commonNames } = data;

	const { form, enhance, errors, message, submitting } = superForm(data.form, {
		invalidateAll: true,
		applyAction: true,
		resetForm: false
	});

	let results: Record<string, any>[] = $derived($message?.results ?? []);
	let headers: string[] = $derived($message?.headers ?? []);
	let apiError: string | null = $derived($message?.apiError ?? $message?.text ?? null);
	let selectedTaskName: string = $derived($message?.selectedTaskName ?? queryTasks[0].name);

	// Find the definition of the currently selected task
	let selectedTaskDefinition = $derived(
		queryTasks.find((task) => task.id === $form.selectedTaskId)
	);
</script>

<div class="container mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
	<!-- Back Link -->
	<div class="mb-6">
		<a href="/admin" class="text-sm text-green-700 hover:text-green-600 hover:underline">
			&larr; Back to Admin Dashboard
		</a>
	</div>

	<h1 class="mb-6 text-3xl font-bold tracking-tight text-gray-900">Run Query Reports</h1>

	<!-- Query Selection Form -->
	<section class="mb-8 rounded-lg bg-white p-6 shadow-md">
		<form method="POST" action="?/runQuery" use:enhance class="space-y-4">
			<div class="flex flex-wrap items-end gap-4">
				<div class="form-control w-full flex-grow sm:w-auto">
					<label for="query-select" class="label">
						<span class="label-text">Select Query Report</span>
					</label>
					<select
						id="query-select"
						name="selectedTaskId"
						bind:value={$form.selectedTaskId}
						class="select select-bordered w-full {$errors.selectedTaskId ? 'select-error' : ''}"
						disabled={$submitting}
					>
						{#each queryTasks as task (task.id)}
							<option value={task.id}>{task.name}</option>
						{/each}
					</select>
					{#if $errors.selectedTaskId}
						<label class="label">
							<span class="label-text-alt text-error">{$errors.selectedTaskId}</span>
						</label>
					{/if}
				</div>

				{#if selectedTaskDefinition?.parameter === 'neighborhood'}
					<div class="form-control w-full flex-grow sm:w-auto">
						<label for="neighborhood-select" class="label">
							<span class="label-text">Neighborhood</span>
						</label>
						<select
							id="neighborhood-select"
							name="neighborhood"
							bind:value={$form.neighborhood}
							class="select select-bordered w-full {$errors.neighborhood ? 'select-error' : ''}"
							disabled={$submitting || neighborhoods.length === 0}
							required
						>
							<option value={undefined} disabled selected>Select a neighborhood...</option>
							{#each neighborhoods as hood (hood)}
								<option value={hood}>{hood}</option>
							{/each}
						</select>
						{#if $errors.neighborhood}
							<label class="label">
								<span class="label-text-alt text-error">{$errors.neighborhood}</span>
							</label>
						{/if}
						{#if neighborhoods.length === 0}
							<label class="label">
								<span class="label-text-alt text-warning">Could not load neighborhoods.</span>
							</label>
						{/if}
					</div>
				{:else if selectedTaskDefinition?.parameter === 'year'}
					<div class="form-control w-full flex-grow sm:w-auto">
						<label for="year-input" class="label">
							<span class="label-text">Year</span>
						</label>
						<input
							type="number"
							id="year-input"
							name="year"
							bind:value={$form.year}
							class="input input-bordered w-full {$errors.year ? 'input-error' : ''}"
							placeholder="Enter year (e.g., {new Date().getFullYear()})"
							disabled={$submitting}
							required
							min="1900"
							max={new Date().getFullYear() + 1}
							step="1"
						/>
						{#if $errors.year}
							<label class="label">
								<span class="label-text-alt text-error">{$errors.year}</span>
							</label>
						{/if}
					</div>
				{:else if selectedTaskDefinition?.parameter === 'common_name'}
					<div class="form-control w-full flex-grow sm:w-auto">
						<label for="common-name-input" class="label">
							<span class="label-text">Tree Common Name</span>
						</label>
						<select
							id="common-name-select"
							name="common_name"
							bind:value={$form.common_name}
							class="select select-bordered w-full {$errors.common_name ? 'select-error' : ''}"
							disabled={$submitting || commonNames.length === 0}
							required
						>
							<option value={undefined} disabled selected>Select a common name...</option>
							{#each commonNames as name (name)}
								<option value={name}>{name}</option>
							{/each}
						</select>
						{#if commonNames.length === 0}
							<label class="label">
								<span class="label-text-alt text-warning">Could not load common names.</span>
							</label>
						{/if}
						{#if $errors.common_name}
							<label class="label">
								<span class="label-text-alt text-error">{$errors.common_name}</span>
							</label>
						{/if}
					</div>
					<!-- Custom Report 4 Parameters -->
				{:else if selectedTaskDefinition?.id === 'custom-report-4'}
					<!-- Min Height -->
					<div class="form-control w-full flex-grow sm:w-auto">
						<label for="min-height-input" class="label">
							<span class="label-text">Min Height (ft)</span>
						</label>
						<input
							type="number"
							id="min-height-input"
							name="min_height"
							bind:value={$form.min_height}
							class="input input-bordered w-full {$errors.min_height ? 'input-error' : ''}"
							placeholder="e.g., 10"
							disabled={$submitting}
							required
							min="0"
							step="any"
						/>
						{#if $errors.min_height}
							<label class="label">
								<span class="label-text-alt text-error">{$errors.min_height}</span>
							</label>
						{/if}
					</div>
					<!-- Max Height -->
					<div class="form-control w-full flex-grow sm:w-auto">
						<label for="max-height-input" class="label">
							<span class="label-text">Max Height (ft)</span>
						</label>
						<input
							type="number"
							id="max-height-input"
							name="max_height"
							bind:value={$form.max_height}
							class="input input-bordered w-full {$errors.max_height ? 'input-error' : ''}"
							placeholder="e.g., 50"
							disabled={$submitting}
							required
							min="0"
							step="any"
						/>
						{#if $errors.max_height}
							<label class="label">
								<span class="label-text-alt text-error">{$errors.max_height}</span>
							</label>
						{/if}
					</div>
					<!-- Min Width -->
					<div class="form-control w-full flex-grow sm:w-auto">
						<label for="min-width-input" class="label">
							<span class="label-text">Min Width (ft)</span>
						</label>
						<input
							type="number"
							id="min-width-input"
							name="min_width"
							bind:value={$form.min_width}
							class="input input-bordered w-full {$errors.min_width ? 'input-error' : ''}"
							placeholder="e.g., 5"
							disabled={$submitting}
							required
							min="0"
							step="any"
						/>
						{#if $errors.min_width}
							<label class="label">
								<span class="label-text-alt text-error">{$errors.min_width}</span>
							</label>
						{/if}
					</div>
					<!-- Max Width -->
					<div class="form-control w-full flex-grow sm:w-auto">
						<label for="max-width-input" class="label">
							<span class="label-text">Max Width (ft)</span>
						</label>
						<input
							type="number"
							id="max-width-input"
							name="max_width"
							bind:value={$form.max_width}
							class="input input-bordered w-full {$errors.max_width ? 'input-error' : ''}"
							placeholder="e.g., 30"
							disabled={$submitting}
							required
							min="0"
							step="any"
						/>
						{#if $errors.max_width}
							<label class="label">
								<span class="label-text-alt text-error">{$errors.max_width}</span>
							</label>
						{/if}
					</div>
				{/if}

				<button type="submit" class="btn btn-primary" disabled={$submitting}>
					{#if $submitting}
						<span class="loading loading-spinner loading-xs"></span>
						Running...
					{:else}
						Run Query
					{/if}
				</button>
			</div>
		</form>
	</section>

	<!-- Results Section -->
	<section class="overflow-hidden rounded-lg bg-white shadow-md">
		<div class="border-b border-gray-200 px-4 py-5 sm:px-6">
			<h2 class="text-xl leading-6 font-semibold text-gray-900">
				Results for: <span class="font-normal">{selectedTaskName}</span>
			</h2>
		</div>
		<div class="p-6">
			{#if $submitting}
				<div class="flex justify-center p-8">
					<span class="loading loading-lg loading-dots text-primary"></span>
				</div>
			{:else if apiError}
				<div class="alert alert-error shadow-lg">
					<div>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="h-6 w-6 flex-shrink-0 stroke-current"
							fill="none"
							viewBox="0 0 24 24"
							><path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M10 14l2-2m0 0l2-2m-2 2l-2 2m2-2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
							/></svg
						>
						<span>Error! {apiError}</span>
					</div>
				</div>
			{:else if results.length > 0 && headers.length > 0}
				<div class="overflow-x-auto rounded-lg border border-gray-200">
					<table class="table-zebra table w-full">
						<thead class="bg-gray-50">
							<tr>
								{#each headers as header}
									<th
										class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
									>
										{header.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
									</th>
								{/each}
							</tr>
						</thead>
						<tbody class="divide-y divide-gray-200 bg-white">
							{#each results as row (row.id ?? JSON.stringify(row))}
								<tr>
									{#each headers as header}
										<td class="px-6 py-4 text-sm whitespace-nowrap text-gray-700">
											{row[header] ?? 'N/A'}
										</td>
									{/each}
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{:else}
				<p class="text-center text-sm text-gray-500">
					{#if $message}
						<!-- Check if a message exists (meaning a query was run) -->
						No results found for this query.
					{:else}
						Select a query and click "Run Query" to see results.
					{/if}
				</p>
			{/if}
		</div>
	</section>
</div>
