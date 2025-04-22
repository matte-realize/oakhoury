<script lang="ts">
	import { enhance } from '$app/forms';
	let { data } = $props();
</script>

<div class="container mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
	<!-- Header Section -->
	<div class="mb-2 flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
		<h1 class="text-3xl font-bold tracking-tight text-gray-900">My Tree Requests</h1>
		<!-- Group buttons together -->
		<div class="flex items-center gap-3">
			<a
				href="/plant"
				class="btn btn-primary inline-flex items-center rounded-md bg-green-700 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-green-600 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 focus:outline-none"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="mr-2 -ml-1 h-5 w-5"
					viewBox="0 0 20 20"
					fill="currentColor"
					aria-hidden="true"
				>
					<path
						fill-rule="evenodd"
						d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z"
						clip-rule="evenodd"
					/>
				</svg>
				Request a New Tree
			</a>

			{#if !data.user.isVolunteer}
				<a
					href="/volunteer-request"
					class="btn transition-color bg-blue-700 text-white shadow-md hover:bg-blue-600"
				>
					Become a volunteer!
				</a>
			{/if}

			<!-- Logout Form -->
			<form method="POST" action="?/logout" use:enhance>
				<button
					type="submit"
					class="btn btn-outline inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:outline-none"
				>
					Logout
				</button>
			</form>
		</div>
	</div>

	<p class="p-3 text-sm font-semibold text-neutral-700">
		{#if data.user.isVolunteer}
			Status: Volunteer
		{:else}
			Status: Resident (If you've recently been approved for being a volunteer, log out and log back
			in.)
		{/if}
	</p>
	<!-- Tree Requests List -->
	<div class="space-y-4">
		{#each data.treeRequests as treeRequest (treeRequest.id)}
			<a
				href="details/{treeRequest.id}"
				class="block rounded-lg border border-gray-200 {treeRequest.approved
					? 'bg-green-200'
					: 'bg-red-200'} p-6 shadow-sm transition-shadow duration-200 hover:shadow-md"
			>
				<div class="flex flex-col justify-between sm:flex-row">
					<div>
						<h2 class="mb-1 text-xl font-semibold text-gray-800">
							Request #{treeRequest.id} - Submitted {new Date(
								treeRequest.submission_timestamp
							).toLocaleDateString()}
						</h2>
						<p class="text-sm text-gray-600">Approved: {treeRequest.approved ? 'Yes' : 'No'}</p>
					</div>
					<div class="mt-2 text-right sm:mt-0">
						<span class="text-sm font-medium text-green-700 hover:text-green-600"
							>View Details →</span
						>
					</div>
				</div>
			</a>
		{:else}
			<!-- Empty State -->
			<div class="rounded-lg border-2 border-dashed border-gray-300 bg-white p-12 text-center">
				<svg
					class="mx-auto h-12 w-12 text-gray-400"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
					aria-hidden="true"
				>
					<path
						vector-effect="non-scaling-stroke"
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z"
					/>
				</svg>
				<h3 class="mt-2 text-sm font-semibold text-gray-900">No tree requests yet</h3>
				<p class="mt-1 text-sm text-gray-500">Get started by requesting your first tree.</p>
				<div class="mt-6">
					<a
						href="/plant"
						class="btn btn-primary inline-flex items-center rounded-md bg-green-700 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
					>
						Request a New Tree
					</a>
				</div>
			</div>
		{/each}
	</div>
</div>
