<script lang="ts">
	import { superForm } from 'sveltekit-superforms';

	let { data } = $props();

	const form = superForm(data.form, {
		multipleSubmits: 'prevent'
	});

	const { enhance, message } = form;

	type PendingApplication = {
		application_id: number;
		resident_id: number;
		created: string;
		notes: string | null;
		first_name: string;
		last_name: string;
		email: string;
	};

	const pendingApplications: PendingApplication[] = data.pendingApplications || [];

	function formatDate(dateString: string | Date) {
		return new Date(dateString).toLocaleDateString();
	}
</script>

<div class="container mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
	<div class="mb-6">
		<a href="/admin" class="text-sm text-green-700 hover:text-green-600 hover:underline">
			&larr; Back to Dashboard
		</a>
	</div>
	<h1 class="mb-8 text-3xl font-bold tracking-tight text-gray-900">Approve Volunteers</h1>

	{#if $message}
		<div class="alert mb-4 shadow-lg">
			<div>
				<span>{$message}</span>
			</div>
		</div>
	{/if}

	{#if pendingApplications.length > 0}
		<div class="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-md">
			<table class="table-zebra table w-full">
				<thead class="bg-gray-50">
					<tr>
						<th
							class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
							>Name</th
						>
						<th
							class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
							>Email</th
						>
						<th
							class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
							>Date Submitted</th
						>
						<th
							class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
							>Notes</th
						>
						<th
							class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
							>Action</th
						>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-200">
					{#each pendingApplications as app (app.application_id)}
						<tr>
							<td class="px-6 py-4 text-sm font-medium whitespace-nowrap text-gray-900">
								{app.first_name}
								{app.last_name}
							</td>
							<td class="px-6 py-4 text-sm whitespace-nowrap text-gray-500">{app.email}</td>
							<td class="px-6 py-4 text-sm whitespace-nowrap text-gray-500"
								>{formatDate(app.created)}</td
							>
							<td class="px-6 py-4 text-sm text-gray-500">{app.notes || 'N/A'}</td>
							<td class="px-6 py-4 text-sm font-medium whitespace-nowrap">
								<form method="POST" action="?/approveVolunteer" use:enhance>
									<input type="hidden" name="residentId" value={app.resident_id} />
									<button type="submit" class="btn btn-xs btn-success"> Approve </button>
								</form>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{:else}
		<div class="rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
			<!-- Empty state SVG -->
			<svg
				class="mx-auto h-12 w-12 text-gray-400"
				fill="none"
				viewBox="0 0 24 24"
				stroke="currentColor"
				aria-hidden="true"
				><path
					vector-effect="non-scaling-stroke"
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.94-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.06 2.772m0 0a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z"
				/></svg
			>
			<h3 class="mt-2 text-sm font-semibold text-gray-900">No pending volunteer applications</h3>
			<p class="mt-1 text-sm text-gray-500">All applications have been reviewed.</p>
		</div>
	{/if}
</div>
