<script lang="ts">
	import { enhance } from '$app/forms';

	let { data } = $props();
</script>

<div class="container mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
	<div class="mb-8 flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
		<h1 class="text-3xl font-bold tracking-tight text-gray-900">Admin Dashboard</h1>
		<div class="flex flex-wrap gap-3">
			<a
				href="/admin/volunteer-applications"
				class="btn inline-flex items-center rounded-md bg-green-700 px-4 py-2 text-sm font-medium text-white shadow-sm focus:ring-2 focus:ring-offset-2 focus:outline-none"
			>
				Approve Volunteers
			</a>
			<!-- New Button for Query Reports -->
			<a
				href="/admin/query-reports"
				class="btn btn-info inline-flex items-center rounded-md px-4 py-2 text-sm font-medium text-white shadow-sm focus:ring-2 focus:ring-offset-2 focus:outline-none"
			>
				Run Reports
			</a>
			<!-- New button for changing tree inventory -->
			<a
				href="/admin/manage-inventory"
				class="btn inline-flex items-center rounded-md bg-amber-700 px-4 py-2 text-sm font-medium text-white shadow-sm focus:ring-2 focus:ring-offset-2 focus:outline-none"
			>
				Manage Tree Inventory
			</a>
		</div>
	</div>
	<!-- Section for Pending Tree Requests -->
	<section class="mb-10 overflow-hidden rounded-lg bg-white shadow-md">
		<div class="border-b border-gray-200 px-4 py-5 sm:px-6">
			<h2 class="text-xl leading-6 font-semibold text-gray-900">Pending Tree Requests</h2>
			<p class="mt-1 text-sm text-gray-500">Review and manage requests awaiting action.</p>
		</div>
		<div class="p-6">
			{#if data.treeRequests.length > 0}
				<div class="overflow-x-auto rounded-lg border border-gray-200">
					<table class="table-zebra table w-full">
						<thead class="bg-gray-50">
							<tr>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
								>
									Request ID
								</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
								>
									Status
								</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
								>
									Date submitted
								</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
								>
									Actions
								</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-gray-200 bg-white">
							{#each data.treeRequests as request (request.id)}
								<tr>
									<td class="px-6 py-4 text-sm font-medium whitespace-nowrap text-gray-900">
										{request.id}
									</td>
									<td class="px-6 py-4 text-sm whitespace-nowrap text-gray-500">
										<span
											class="badge"
											class:badge-warning={request.status === 'pending approval' ||
												request.status === 'needs permit'}
											class:badge-info={request.status === 'waiting for visit'}
											class:badge-success={request.status === 'waiting for planting'}
											class:badge-error={request.status === 'denied'}
											class:badge-ghost={![
												'pending approval',
												'needs permit',
												'waiting for visit',
												'waiting for planting',
												'denied'
											].includes(request.status)}
										>
											{request.status}
										</span>
									</td>
									<td class="px-6 py-4 text-sm whitespace-nowrap text-gray-500">
										{new Date(request.submission_timestamp).toLocaleDateString()}
									</td>
									<td class="px-6 py-4 text-sm font-medium whitespace-nowrap">
										<div class="flex items-center gap-2">
											<!-- Link to details page -->
											<a class="btn btn-xs btn-outline btn-info" href="/admin/details/{request.id}">
												Details
											</a>
											<!-- Approve/Deny Action Form -->
											{#if request.status === 'pending approval'}
												<form method="POST" action="?/approveRequest" use:enhance>
													<input type="hidden" name="requestId" value={request.id} />
													<button type="submit" class="btn btn-xs btn-success"> Approve </button>
												</form>
												<form method="POST" action="?/denyRequest" use:enhance>
													<input type="hidden" name="requestId" value={request.id} />
													<button type="submit" class="btn btn-xs btn-success"> Deny </button>
												</form>
											{/if}
										</div>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{:else}
				<div class="rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
					<svg
						class="mx-auto h-12 w-12 text-gray-400"
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
						stroke-width="1.5"
						stroke="currentColor"
						aria-hidden="true"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
						/>
					</svg>

					<h3 class="mt-2 text-sm font-semibold text-gray-900">No pending requests</h3>
					<p class="mt-1 text-sm text-gray-500">All tree requests are up to date.</p>
				</div>
			{/if}
		</div>
	</section>

	<!-- TODO: add report content -->
</div>
