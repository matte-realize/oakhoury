<script lang="ts">
	import { superForm } from 'sveltekit-superforms';
	import { zod } from 'sveltekit-superforms/adapters';
	import { z } from 'zod';

	let { data } = $props();
	const {
		plantingDetails,
		availableVolunteers,
		availableOrgMembers,
		assignVolunteerForm: assignVolunteerFormData,
		assignOrgMemberForm: assignOrgMemberFormData,
		recordOutcomeForm: recordOutcomeFormData,
		plantingEventId
	} = data;

	type Person = { id: number; first_name: string; last_name: string };
	type PlantingDetails = {
		event_id: number;
		tree_request_id: number;
		event_timestamp: string;
		cancelled: boolean;
		notes: string | null;
		site_description: string | null;
		assigned_volunteers: Person[];
		assigned_org_members: Person[];
		outcome_recorded: boolean;
		outcome_successful?: boolean;
		outcome_observations?: string | null;
		attended_volunteers?: Person[];
	};

	const details: PlantingDetails = plantingDetails;

	const assignVolunteerSchema = z.object({
		volunteerId: z.coerce.number().int().positive('Please select a volunteer.')
	});
	const assignOrgMemberSchema = z.object({
		orgMemberId: z.coerce.number().int().positive('Please select an organization member.')
	});
	const recordOutcomeSchema = z.object({
		successful: z.boolean({ required_error: 'Please indicate if the planting was successful.' }),
		observations: z.string().optional(),
		attended_volunteer_ids: z.array(z.coerce.number().int().positive()).optional().default([])
	});

	const assignVolunteerForm = superForm(assignVolunteerFormData, {
		validators: zod(assignVolunteerSchema),
		id: 'assignVolunteerForm',
		invalidateAll: true,
		resetForm: true
	});
	const assignOrgMemberForm = superForm(assignOrgMemberFormData, {
		validators: zod(assignOrgMemberSchema),
		id: 'assignOrgMemberForm',
		invalidateAll: true,
		resetForm: true
	});
	const recordOutcomeForm = superForm(recordOutcomeFormData, {
		validators: zod(recordOutcomeSchema),
		id: 'recordOutcomeForm',
		dataType: 'json'
	});

	const {
		form: assignVolFormData,
		enhance: enhanceVol,
		message: messageVol,
		errors: errorsVol
	} = assignVolunteerForm;
	const {
		form: assignOrgFormData,
		enhance: enhanceOrg,
		message: messageOrg,
		errors: errorsOrg
	} = assignOrgMemberForm;
	const {
		form: outcomeFormData,
		enhance: enhanceOutcome,
		message: messageOutcome,
		errors: errorsOutcome
	} = recordOutcomeForm;

	const assignedVolunteerIds = new Set(details.assigned_volunteers.map((v) => v.id));
	const assignedOrgMemberIds = new Set(details.assigned_org_members.map((m) => m.id));

	const filteredAvailableVolunteers = availableVolunteers.filter(
		(v: Person) => !assignedVolunteerIds.has(v.id)
	);
	const filteredAvailableOrgMembers = availableOrgMembers.filter(
		(m: Person) => !assignedOrgMemberIds.has(m.id)
	);

	function formatDate(dateString: string | Date) {
		return new Date(dateString).toLocaleString();
	}
</script>

<div class="container mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
	<!-- Back Link -->
	<div class="mb-6">
		<a
			href="/admin/details/{details.tree_request_id}"
			class="text-sm text-green-700 hover:text-green-600 hover:underline"
		>
			&larr; Back to Request Details (ID: {details.tree_request_id})
		</a>
	</div>

	<h1 class="mb-6 text-3xl font-bold tracking-tight text-gray-900">
		Manage Planting Event - ID: {plantingEventId}
		{#if details.cancelled}
			<span class="badge badge-lg badge-error ml-4">Cancelled</span>
		{/if}
	</h1>

	<!-- Planting Details Card -->
	<section class="mb-8 overflow-hidden rounded-lg bg-white shadow-md">
		<div class="border-b border-gray-200 px-4 py-5 sm:px-6">
			<h2 class="text-xl leading-6 font-semibold text-gray-900">Event Details</h2>
		</div>
		<div class="p-6">
			<dl class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
				<div class="sm:col-span-1">
					<dt class="text-sm font-medium text-gray-500">Date & Time</dt>
					<dd class="mt-1 text-sm text-gray-900">{formatDate(details.event_timestamp)}</dd>
				</div>
				<div class="sm:col-span-1">
					<dt class="text-sm font-medium text-gray-500">Status</dt>
					<dd class="mt-1 text-sm text-gray-900">
						{#if details.cancelled}
							Cancelled
						{:else if details.outcome_recorded}
							{#if details.outcome_successful}
								<span class="text-success">Successful</span>
							{:else}
								<span class="text-error">Not Successful</span>
							{/if}
						{:else}
							Scheduled{/if}
					</dd>
				</div>
				<div class="sm:col-span-2">
					<dt class="text-sm font-medium text-gray-500">Planting Notes</dt>
					<dd class="mt-1 text-sm text-gray-900">{details.notes || 'N/A'}</dd>
				</div>
				<div class="sm:col-span-2">
					<dt class="text-sm font-medium text-gray-500">Original Request Site Description</dt>
					<dd class="mt-1 text-sm text-gray-900">{details.site_description || 'N/A'}</dd>
				</div>
			</dl>
		</div>
	</section>

	<!-- Assigned People & Actions Card -->
	<section class="mb-8 overflow-hidden rounded-lg bg-white shadow-md">
		<div class="border-b border-gray-200 px-4 py-5 sm:px-6">
			<h2 class="text-xl leading-6 font-semibold text-gray-900">Assignments & Actions</h2>
		</div>
		<div class="grid grid-cols-1 gap-6 p-6 md:grid-cols-2">
			<!-- Assigned Volunteers -->
			<div>
				<h3 class="mb-3 text-lg font-medium text-gray-800">Assigned Volunteers</h3>
				<!-- Text that tells user that volunteers will be emailed that they have been assigned with relevant info -->

				<p class="text-sm text-gray-500">
					Assigned volunteers will receive an email with the event details.
					{#if details.cancelled}
						<span class="text-error">Note: This event is cancelled.</span>
					{/if}
				</p>
				{#if details.assigned_volunteers.length > 0}
					<ul class="list-disc space-y-1 pl-5 text-sm text-gray-700">
						{#each details.assigned_volunteers as vol (vol.id)}
							<li>{vol.first_name} {vol.last_name}</li>
						{/each}
					</ul>
				{:else}
					<p class="text-sm text-gray-500">No volunteers assigned yet.</p>
				{/if}

				<!-- Assign Volunteer Form -->
				{#if !details.cancelled}
					<form method="POST" action="?/assignVolunteer" use:enhanceVol class="mt-4 space-y-3">
						{#if $messageVol}
							<p class="text-xs {$messageVol.includes('Failed') ? 'text-error' : 'text-success'}">
								{$messageVol}
							</p>
						{/if}
						<label for="volunteerId" class="block text-sm font-medium text-gray-700"
							>Assign New Volunteer</label
						>
						<div class="flex items-center gap-2">
							<select
								id="volunteerId"
								name="volunteerId"
								class="select select-bordered select-sm w-full max-w-xs {$errorsVol.volunteerId
									? 'select-error'
									: ''}"
								bind:value={$assignVolFormData.volunteerId}
								disabled={filteredAvailableVolunteers.length === 0}
							>
								<option disabled selected value={undefined}>Select a volunteer...</option>
								{#each filteredAvailableVolunteers as vol (vol.id)}
									<option value={vol.id}>{vol.first_name} {vol.last_name}</option>
								{/each}
							</select>
							<button
								type="submit"
								class="btn btn-sm btn-primary"
								disabled={filteredAvailableVolunteers.length === 0}
							>
								Assign
							</button>
						</div>
						{#if $errorsVol.volunteerId}
							<p class="text-error text-xs">{$errorsVol.volunteerId}</p>
						{/if}
						{#if filteredAvailableVolunteers.length === 0 && details.assigned_volunteers.length > 0}
							<p class="text-xs text-gray-500">All available volunteers are assigned.</p>
						{/if}
					</form>
				{/if}
			</div>

			<!-- Assigned Org Members -->
			<div>
				<h3 class="mb-3 text-lg font-medium text-gray-800">Assigned Org Members (Leads)</h3>
				{#if details.assigned_org_members.length > 0}
					<ul class="list-disc space-y-1 pl-5 text-sm text-gray-700">
						{#each details.assigned_org_members as mem (mem.id)}
							<li>{mem.first_name} {mem.last_name}</li>
						{/each}
					</ul>
				{:else}
					<p class="text-sm text-gray-500">No organization members assigned yet.</p>
				{/if}

				<!-- Assign Org Member Form -->
				{#if !details.cancelled}
					<form method="POST" action="?/assignOrgMember" use:enhanceOrg class="mt-4 space-y-3">
						{#if $messageOrg}
							<p class="text-xs {$messageOrg.includes('Failed') ? 'text-error' : 'text-success'}">
								{$messageOrg}
							</p>
						{/if}
						<label for="orgMemberId" class="block text-sm font-medium text-gray-700"
							>Assign New Org Member</label
						>
						<div class="flex items-center gap-2">
							<select
								id="orgMemberId"
								name="orgMemberId"
								class="select select-bordered select-sm w-full max-w-xs {$errorsOrg.orgMemberId
									? 'select-error'
									: ''}"
								bind:value={$assignOrgFormData.orgMemberId}
								disabled={filteredAvailableOrgMembers.length === 0}
							>
								<option disabled selected value={undefined}>Select an org member...</option>
								{#each filteredAvailableOrgMembers as mem (mem.id)}
									<option value={mem.id}>{mem.first_name} {mem.last_name}</option>
								{/each}
							</select>
							<button
								type="submit"
								class="btn btn-sm btn-primary"
								disabled={filteredAvailableOrgMembers.length === 0}
							>
								Assign
							</button>
						</div>
						{#if $errorsOrg.orgMemberId}
							<p class="text-error text-xs">{$errorsOrg.orgMemberId}</p>
						{/if}
						{#if filteredAvailableOrgMembers.length === 0 && details.assigned_org_members.length > 0}
							<p class="text-xs text-gray-500">All available org members are assigned.</p>
						{/if}
					</form>
				{/if}
			</div>
		</div>
	</section>

	<!-- Record Planting Outcome Section -->
	{#if !details.cancelled && !details.outcome_recorded}
		<section class="mt-8 overflow-hidden rounded-lg bg-white shadow-md">
			<div class="border-b border-gray-200 px-4 py-5 sm:px-6">
				<h2 class="text-xl leading-6 font-semibold text-gray-900">Record Planting Outcome</h2>
			</div>
			<form method="POST" action="?/recordOutcome" use:enhanceOutcome class="space-y-6 p-6">
				{#if $messageOutcome}
					<div class="alert shadow-lg">
						<div>
							<span>{$messageOutcome}</span>
						</div>
					</div>
				{/if}

				<!-- Successful Checkbox -->
				<div class="form-control">
					<label class="label cursor-pointer justify-start gap-4">
						<input
							type="checkbox"
							name="successful"
							bind:checked={$outcomeFormData.successful}
							class="checkbox checkbox-primary"
						/>
						<span class="label-text">Planting Successful?</span>
					</label>
					{#if $errorsOutcome.successful}
						<p class="mt-1 text-sm text-red-600">{$errorsOutcome.successful}</p>
					{/if}
				</div>

				<!-- Observations Textarea -->
				<div>
					<label for="observations" class="block text-sm font-medium text-gray-700">
						Observations / Notes (Optional)
					</label>
					<textarea
						id="observations"
						name="observations"
						bind:value={$outcomeFormData.observations}
						rows="4"
						class="textarea textarea-bordered mt-1 block w-full {$errorsOutcome.observations
							? 'textarea-error'
							: ''}"
						placeholder="Enter any notes about the planting event, site conditions, resident interaction, etc."
						aria-invalid={$errorsOutcome.observations ? 'true' : undefined}
					></textarea>
					{#if $errorsOutcome.observations}
						<p class="mt-2 text-sm text-red-600">{$errorsOutcome.observations}</p>
					{/if}
				</div>

				<!-- Attended Volunteers Checkboxes -->
				{#if details.assigned_volunteers.length > 0}
					<div>
						<label class="block text-sm font-medium text-gray-700"> Attended Volunteers </label>
						<div class="mt-2 space-y-2 rounded-md border border-gray-200 p-4">
							{#each details.assigned_volunteers as vol (vol.id)}
								<div class="form-control">
									<label class="label cursor-pointer justify-start gap-3">
										<input
											type="checkbox"
											name="attended_volunteer_ids"
											value={vol.id}
											bind:group={$outcomeFormData.attended_volunteer_ids}
											class="checkbox checkbox-sm"
										/>
										<span class="label-text text-sm">{vol.first_name} {vol.last_name}</span>
									</label>
								</div>
							{/each}
						</div>
						{#if $errorsOutcome.attended_volunteer_ids}
							<p class="mt-2 text-sm text-red-600">{$errorsOutcome.attended_volunteer_ids}</p>
						{/if}
					</div>
				{:else}
					<p class="text-sm text-gray-500">No volunteers were assigned to this planting.</p>
				{/if}

				<!-- Submit Button -->
				<div>
					<button type="submit" class="btn btn-success w-full"> Record Planting Outcome </button>
				</div>
			</form>
		</section>
	{:else if plantingDetails.outcome_recorded}
		<!-- Show Recorded Outcome Details -->
		<section class="mt-8 overflow-hidden rounded-lg bg-white shadow-md">
			<div class="border-b border-gray-200 bg-blue-50 px-4 py-5 sm:px-6">
				<h2 class="text-xl leading-6 font-semibold text-blue-800">Recorded Planting Outcome</h2>
			</div>
			<div class="p-6">
				<dl class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
					<div class="sm:col-span-1">
						<dt class="text-sm font-medium text-gray-500">Outcome</dt>
						<dd class="mt-1 text-sm font-semibold">
							{#if details.outcome_successful}
								<span class="text-success">Successful</span>
							{:else}
								<span class="text-error">Not Successful</span>
							{/if}
						</dd>
					</div>
					<div class="sm:col-span-2">
						<dt class="text-sm font-medium text-gray-500">Observations</dt>
						<dd class="mt-1 text-sm whitespace-pre-wrap text-gray-900">
							{details.outcome_observations || 'N/A'}
						</dd>
					</div>
					<div class="sm:col-span-2">
						<dt class="text-sm font-medium text-gray-500">Volunteers Who Attended</dt>
						<dd class="mt-1 text-sm text-gray-900">
							{#if details.attended_volunteers && details.attended_volunteers.length > 0}
								<ul class="list-disc space-y-1 pl-5">
									{#each details.attended_volunteers as vol (vol.id)}
										<li>{vol.first_name} {vol.last_name}</li>
									{/each}
								</ul>
							{:else}
								No volunteers recorded as attending.
							{/if}
						</dd>
					</div>
				</dl>
			</div>
		</section>
	{/if}
</div>
