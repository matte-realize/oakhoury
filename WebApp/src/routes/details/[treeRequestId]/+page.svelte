<script lang="ts">
	import { superForm } from 'sveltekit-superforms/client';

	const { data } = $props();

	const { form, errors, message, enhance } = superForm(data.form, {
		resetForm: false
	});
	const permitStatuses: App.PermitStatus[] = ['pending', 'approved', 'denied'] as const;
	$form.status = data.permitStatus as App.PermitStatus;
	// Get status and display user friendly text and emoji
	const getStatusDisplay = (): string => {
		switch (data.status as App.TreeRequestStatus) {
			case 'needs permit':
				return '📝 Needs Permit';
			case 'waiting for planting':
				return '🌱 Waiting for Planting';
			case 'waiting for visit':
				return '👀 Waiting for Visit';
			case 'pending approval':
				return '⏳ Pending Approval';
			case 'completed':
				return '✅ Completed';
			case 'denied':
				return '❌ Denied. Check you email for details.';
			default:
				return `❓ Unknown (${data.status})`;
		}
	};

	// Format days since planting
	const formatDays = (days: number | null | undefined): string => {
		if (days === null || days === undefined || isNaN(days)) {
			return 'N/A';
		}
		if (days === 0) {
			return 'Submitted today';
		}
		if (days === 1) {
			return '1 day ago';
		}
		return `${days} days ago`;
	};
</script>

<div class="container mx-auto max-w-2xl px-4 py-12 sm:px-6 lg:px-8">
	<div class="mb-6">
		<a href="/dashboard" class="text-sm text-green-700 hover:text-green-600 hover:underline">
			&larr; Back to Dashboard
		</a>
	</div>

	<div class="overflow-hidden rounded-lg shadow">
		<div class="border-b border-gray-200 bg-white px-4 py-5 sm:px-6">
			<h2 class="text-xl leading-6 font-semibold text-gray-900">Tree Request Details</h2>
			<p class="mt-1 max-w-2xl text-sm text-gray-500">Information about your requested tree.</p>
		</div>
		<div class="border-t border-gray-200 px-4 py-5 sm:p-0">
			<dl class="sm:divide-y sm:divide-gray-200">
				<div class="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 sm:py-5">
					<dt class="text-sm font-medium text-gray-500">Common Name</dt>
					<dd class="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">{data.commonName}</dd>
				</div>
				<div class="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 sm:py-5">
					<dt class="text-sm font-medium text-gray-500">Scientific Name</dt>
					<dd class="mt-1 text-sm text-gray-900 italic sm:col-span-2 sm:mt-0">
						{data.scientificName}
					</dd>
				</div>
				<div class="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 sm:py-5">
					<dt class="text-sm font-medium text-gray-500">Status</dt>
					<dd class="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">{getStatusDisplay()}</dd>
				</div>
				<div class="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 sm:py-5">
					<dt class="text-sm font-medium text-gray-500">Time Since Submitted</dt>
					<dd class="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
						{formatDays(data.daysSincePlanting)}
					</dd>
				</div>
			</dl>
		</div>

		<!-- Permit Status Update Form -->
		{#if !['completed', 'pending approval', 'denied'].includes(data.status)}
			<div class="border-t border-gray-200 px-4 py-5 sm:px-6">
				<!-- Text saying you must now get a permit approved from city of oakland -->
				<p class="mb-4 text-sm text-gray-500">
					To proceed with your request, you must get a permit approved from the city of Oakland.
					Please visit the <a
						href="https://www.oaklandca.gov/services/tree-planting-application"
						class="text-green-700 hover:text-green-600 hover:underline"
						>Oakland Tree Permit Application</a
					> page for more information.
				</p>
				<h3 class="text-lg leading-6 font-medium text-gray-900">Update Permit Status</h3>
				<form method="POST" use:enhance class="mt-4 space-y-4">
					<div>
						<label for="status" class="block text-sm font-medium text-gray-700">New Status</label>
						<select
							id="status"
							name="status"
							bind:value={$form.status}
							class="mt-1 block w-full rounded-md border-gray-300 py-2 pr-10 pl-3 text-base focus:border-indigo-500 focus:ring-indigo-500 focus:outline-none sm:text-sm {$errors.status
								? 'border-red-500'
								: ''}"
							aria-invalid={$errors.status ? 'true' : undefined}
							aria-describedby={$errors.status ? 'status-error' : undefined}
						>
							{#each permitStatuses as e}
								<option value={e}>{e}</option>
							{/each}
						</select>
						{#if $errors.status}
							<p class="mt-2 text-sm text-red-600" id="status-error">{$errors.status}</p>
						{/if}
					</div>
					<div>
						<button
							type="submit"
							class="inline-flex justify-center rounded-md border border-transparent bg-green-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 focus:outline-none disabled:opacity-50"
						>
							Update Permit Status
						</button>
					</div>
					{#if $message}
						<p class="text-sm text-green-600">{$message}</p>
					{/if}
				</form>
			</div>
		{/if}
	</div>
</div>
