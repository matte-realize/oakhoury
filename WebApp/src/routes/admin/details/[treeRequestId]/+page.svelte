<script lang="ts">
	import { page } from '$app/state';

	let { data } = $props();
	const { treeRequestId } = page.params;
	const { requestDetails, scheduledVisits, scheduledPlantings } = data;

	type ScheduledVisit = {
		event_id: number;
		event_timestamp: string;
		cancelled: boolean;
		notes: string | null;
		organization_member_id: number | null;
		outcome_recorded: boolean;
	};

	const visits: ScheduledVisit[] = scheduledVisits;

	const formatDate = (dateString: string | Date) => {
		return new Date(dateString).toLocaleString();
	};
</script>

<div class="container mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
	<div class="mb-6">
		<a href="/admin" class="text-sm text-green-700 hover:text-green-600 hover:underline">
			&larr; Back to Dashboard
		</a>
	</div>
	<h1 class="mb-6 text-3xl font-bold tracking-tight text-gray-900">
		Tree Request Details - ID: {treeRequestId}
	</h1>

	<!-- Request Information Card -->
	<section class="mb-8 overflow-hidden rounded-lg bg-white shadow-md">
		<div class="border-b border-gray-200 px-4 py-5 sm:px-6">
			<h2 class="text-xl leading-6 font-semibold text-gray-900">Request Information</h2>
		</div>
		<div class="p-6">
			<dl class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
				<div class="sm:col-span-1">
					<dt class="text-sm font-medium text-gray-500">Tree Species</dt>
					<dd class="mt-1 text-sm text-gray-900">
						{requestDetails.tree_common_name} (<em>{requestDetails.tree_scientific_name}</em>)
					</dd>
				</div>
				<div class="sm:col-span-1">
					<dt class="text-sm font-medium text-gray-500">Current Inventory</dt>
					<dd class="mt-1 text-sm text-gray-900">{requestDetails.tree_inventory}</dd>
				</div>
				<div class="sm:col-span-1">
					<dt class="text-sm font-medium text-gray-500">Resident Address</dt>
					<dd class="mt-1 text-sm text-gray-900">
						{requestDetails.resident_street}, {requestDetails.resident_neighborhood}, {requestDetails.resident_zip_code}
					</dd>
				</div>
				<div class="sm:col-span-1">
					<dt class="text-sm font-medium text-gray-500">Status</dt>
					<dd class="mt-1 text-sm text-gray-900">
						<span
							class="badge"
							class:badge-warning={requestDetails.status === 'pending approval' ||
								requestDetails.status === 'needs permit'}
							class:badge-info={requestDetails.status === 'waiting for visit' ||
								requestDetails.status === 'approved'}
							class:badge-success={requestDetails.status === 'waiting for planting' ||
								requestDetails.status === 'completed'}
							class:badge-error={requestDetails.status === 'denied'}
							class:badge-ghost={![
								'pending approval',
								'needs permit',
								'waiting for visit',
								'approved',
								'waiting for planting',
								'completed',
								'denied'
							].includes(requestDetails.status)}
						>
							{requestDetails.status}
						</span>
					</dd>
				</div>
				<div class="sm:col-span-2">
					<dt class="text-sm font-medium text-gray-500">Site Description / Notes</dt>
					<dd class="mt-1 text-sm text-gray-900">{requestDetails.site_description || 'N/A'}</dd>
				</div>
			</dl>
		</div>
	</section>

	<!-- Actions Card -->
	<section class="mb-8 overflow-hidden rounded-lg bg-white shadow-md">
		<div class="border-b border-gray-200 px-4 py-5 sm:px-6">
			<h2 class="text-xl leading-6 font-semibold text-gray-900">Actions</h2>
		</div>
		<div class="flex flex-wrap gap-4 p-6">
			<!-- TODO: conditional on status -->
			<a href="/admin/schedule-visit/{treeRequestId}" class="btn btn-primary"> Schedule Visit </a>
			<a href="/admin/schedule-planting/{treeRequestId}" class="btn btn-secondary">
				Schedule Planting
			</a>
		</div>
	</section>

	<!-- Scheduled Visits Table -->
	<section class="mb-8 overflow-hidden rounded-lg bg-white shadow-md">
		<div class="border-b border-gray-200 px-4 py-5 sm:px-6">
			<h2 class="text-xl leading-6 font-semibold text-gray-900">Scheduled Visits</h2>
		</div>
		<div class="p-6">
			{#if visits.length > 0}
				<div class="overflow-x-auto rounded-lg border border-gray-200">
					<table class="table-zebra table w-full">
						<thead class="bg-gray-50">
							<tr>
								<th>Visit ID</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
									>Date/Time</th
								>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
									>Status</th
								>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
									>Org Member ID</th
								>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
									>Notes</th
								>

								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
								>
									Actions
								</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-gray-200 bg-white">
							{#each visits as visit (visit.event_id)}
								<tr>
									<td class="px-6 py-4 text-sm font-medium whitespace-nowrap text-gray-900"
										>{visit.event_id}</td
									>
									<td class="px-6 py-4 text-sm whitespace-nowrap text-gray-500"
										>{formatDate(visit.event_timestamp)}</td
									>
									<td class="px-6 py-4 text-sm whitespace-nowrap text-gray-500">
										{#if visit.cancelled}
											<span class="badge badge-error">Cancelled</span>
										{:else if visit.outcome_recorded}
											<span class="badge badge-primary">Completed</span>
											<!-- Show Completed status -->
										{:else}
											<span class="badge badge-success">Scheduled</span>
										{/if}
									</td>
									<td class="px-6 py-4 text-sm whitespace-nowrap text-gray-500"
										>{visit.organization_member_id || 'N/A'}</td
									>
									<td class="px-6 py-4 text-sm text-gray-500">{visit.notes || 'N/A'}</td>
									<!-- Actions Cell -->
									<td class="px-6 py-4 text-sm whitespace-nowrap">
										<!-- Only show button if NOT cancelled AND outcome NOT recorded -->
										{#if !visit.cancelled && !visit.outcome_recorded}
											<a
												href="/admin/record-visit/{visit.event_id}"
												class="btn btn-xs btn-outline btn-info"
											>
												Record Outcome
											</a>
										{:else if visit.outcome_recorded}
											<span class="text-xs text-gray-500 italic">Outcome recorded</span>
										{/if}
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{:else}
				<p class="text-center text-sm text-gray-500">No scheduled visits for this request.</p>
			{/if}
		</div>
	</section>

	<!-- Scheduled Plantings Table -->
	<section class="overflow-hidden rounded-lg bg-white shadow-md">
		<div class="border-b border-gray-200 px-4 py-5 sm:px-6">
			<h2 class="text-xl leading-6 font-semibold text-gray-900">Scheduled Plantings</h2>
		</div>
		<div class="p-6">
			{#if scheduledPlantings.length > 0}
				<div class="overflow-x-auto rounded-lg border border-gray-200">
					<table class="table-zebra table w-full">
						<thead class="bg-gray-50">
							<tr>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
									>Planting ID</th
								>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
									>Date/Time</th
								>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
									>Status</th
								>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
									>Notes</th
								>
							</tr>
						</thead>
						<tbody class="divide-y divide-gray-200 bg-white">
							{#each scheduledPlantings as planting (planting.event_id)}
								<tr>
									<td class="px-6 py-4 text-sm font-medium whitespace-nowrap text-gray-900">
										<a
											href="/admin/manage-planting/{planting.event_id}"
											class="text-green-700 hover:text-green-600 hover:underline"
										>
											{planting.event_id}
										</a>
									</td>
									<td class="px-6 py-4 text-sm whitespace-nowrap text-gray-500"
										>{formatDate(planting.event_timestamp)}</td
									>
									<td class="px-6 py-4 text-sm whitespace-nowrap text-gray-500">
										{#if planting.cancelled}
											<span class="badge badge-error">Cancelled</span>
										{:else if planting.outcome_recorded}
											<span class="badge badge-primary">Completed</span>
										{:else}
											<span class="badge badge-success">Scheduled</span>
										{/if}
									</td>
									<td class="px-6 py-4 text-sm text-gray-500">{planting.notes || 'N/A'}</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{:else}
				<p class="text-center text-sm text-gray-500">No scheduled plantings for this request.</p>
			{/if}
		</div>
	</section>
</div>
