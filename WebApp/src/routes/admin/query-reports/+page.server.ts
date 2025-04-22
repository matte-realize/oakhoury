import { API_ROUTE } from '$lib/constants';
import { error, fail, redirect } from '@sveltejs/kit';
import { message, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { z } from 'zod';
import type { Actions, PageServerLoad } from './$types';

const queryTasks = [
	{
		id: 'task1',
		name: 'Task 1: Pending Requests Status & Age',
		endpoint: '/tree-requests-status'
	},
	{
		id: 'task2',
		name: 'Task 2: Trees Planted by Neighborhood',
		endpoint: '/trees-planted',
		parameter: 'neighborhood'
	},
	{
		id: 'task3',
		name: 'Task 3: Tree Species Statistics',
		endpoint: '/tree-species-statistics'
	},
	{
		id: 'task4',
		name: 'Task 4: Neighborhood Report',
		endpoint: '/neighborhood-report'
	},
	{
		id: 'custom-report-1',
		name: 'Custom 1: Volunteer Planting Activity by Year',
		endpoint: '/custom-report-1',
		parameter: 'year'
	},
	{
		id: 'custom-report-2',
		name: 'Custom 2: Org Member Activity by Year',
		endpoint: '/custom-report-2',
		parameter: 'year'
	},
	{
		id: 'custom-report-3',
		name: 'Custom 3: Tree Planting Locations by Species',
		endpoint: '/custom-report-3',
		parameter: 'common_name'
	},
	{
		id: 'custom-report-4',
		name: 'Custom 4: Find Trees by Size',
		endpoint: '/custom-report-4',
		parameters: ['min_height', 'max_height', 'min_width', 'max_width']
	},
	{
		id: 'custom-report-5',
		name: 'Custom 5: Volunteer success rate',
		endpoint: '/custom-report-5'
	}
];

const queryFormSchema = z
	.object({
		selectedTaskId: z.string().min(1, 'Please select a query task.'),
		neighborhood: z.string().optional(),
		year: z.coerce
			.number({ invalid_type_error: 'Year must be a number.' })
			.int({ message: 'Year must be a whole number.' })
			.min(1900, { message: 'Year seems too early.' })
			.max(new Date().getFullYear() + 1, { message: 'Year cannot be in the future.' })
			.optional(),
		common_name: z.string().optional(),
		min_height: z.coerce
			.number({ invalid_type_error: 'Min height must be a number.' })
			.positive({ message: 'Min height must be positive.' })
			.optional(),
		max_height: z.coerce
			.number({ invalid_type_error: 'Max height must be a number.' })
			.positive({ message: 'Max height must be positive.' })
			.optional(),
		min_width: z.coerce
			.number({ invalid_type_error: 'Min width must be a number.' })
			.positive({ message: 'Min width must be positive.' })
			.optional(),
		max_width: z.coerce
			.number({ invalid_type_error: 'Max width must be a number.' })
			.positive({ message: 'Max width must be positive.' })
			.optional()
	})
	.superRefine((data, ctx) => {
		const task = queryTasks.find((t) => t.id === data.selectedTaskId);
		if (!task) return; // Should not happen if task ID is valid

		// Handle single parameter tasks
		if (task.parameter) {
			const paramValue = data[task.parameter as keyof typeof data];
			let isValid = false;
			switch (task.parameter) {
				case 'neighborhood':
					isValid = typeof paramValue === 'string' && paramValue.trim().length > 0;
					break;
				case 'year':
					isValid = paramValue !== undefined && paramValue !== null; // Basic check, type handled by coerce
					break;
				case 'common_name':
					isValid = typeof paramValue === 'string' && paramValue.trim().length > 0;
					break;
			}
			if (!isValid) {
				const paramName = task.parameter
					.replace(/_/g, ' ')
					.replace(/\b\w/g, (l) => l.toUpperCase());
				ctx.addIssue({
					code: z.ZodIssueCode.custom,
					message: `${paramName} is required for ${task.name}.`,
					path: [task.parameter]
				});
			}
		}
		// Handle multi-parameter task (Custom Report 4)
		else if (task.id === 'custom-report-4') {
			const requiredParams = ['min_height', 'max_height', 'min_width', 'max_width'];
			let allParamsValid = true;
			for (const param of requiredParams) {
				const value = data[param as keyof typeof data];
				if (value === undefined || value === null) {
					allParamsValid = false;
					const paramName = param.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
					ctx.addIssue({
						code: z.ZodIssueCode.custom,
						message: `${paramName} is required for ${task.name}.`,
						path: [param]
					});
				}
			}
			// Add cross-field validation (e.g., min <= max)
			if (allParamsValid) {
				if (data.min_height! > data.max_height!) {
					ctx.addIssue({
						code: z.ZodIssueCode.custom,
						message: 'Min height cannot be greater than Max height.',
						path: ['min_height'] // Or ['max_height']
					});
				}
				if (data.min_width! > data.max_width!) {
					ctx.addIssue({
						code: z.ZodIssueCode.custom,
						message: 'Min width cannot be greater than Max width.',
						path: ['min_width'] // Or ['max_width']
					});
				}
			}
		}
	});

export const load: PageServerLoad = async ({ locals, fetch }) => {
	if (!locals.user) {
		throw redirect(303, '/login?redirectTo=/admin/query-reports');
	}
	const isMemberApiUrl = `${API_ROUTE}/is_organization_member?user_id=${encodeURIComponent(locals.user.id)}`;
	const isMemberResponse = await fetch(isMemberApiUrl);
	if (!isMemberResponse.ok) {
		throw error(500, 'Failed to verify user role.');
	}
	const { is_organization_member } = await isMemberResponse.json();
	if (!is_organization_member) {
		throw error(403, 'Forbidden: You do not have permission to access this page.');
	}

	let neighborhoods: string[] = [];
	const neighborhoodsRes = await fetch(`${API_ROUTE}/neighborhoods`);
	if (neighborhoodsRes.ok) {
		neighborhoods = await neighborhoodsRes.json();
	}

	let commonNames: string[] = [];
	const namesRes = await fetch(`${API_ROUTE}/trees`);
	if (namesRes.ok) {
		const treesData = await namesRes.json();
		commonNames = treesData.map((tree: { common_name: string }) => tree.common_name);
	}

	const form = await superValidate(zod(queryFormSchema), {
		defaults: { selectedTaskId: queryTasks[0].id }
	});

	return { form, queryTasks, neighborhoods, commonNames };
};

export const actions: Actions = {
	runQuery: async ({ request, fetch }) => {
		const form = await superValidate(request, zod(queryFormSchema));

		if (!form.valid) {
			return fail(400, { form });
		}

		const selectedTask = queryTasks.find((task) => task.id === form.data.selectedTaskId);

		if (!selectedTask) {
			return message(form, 'Invalid task selected.', { status: 400 });
		}

		let results: Record<string, unknown>[] = [];
		let headers: string[] = [];
		let apiError: string | null = null;

		let apiUrl = `${API_ROUTE}${selectedTask.endpoint}`;
		const queryParams = new URLSearchParams();

		if (selectedTask.parameter) {
			const paramValue = form.data[selectedTask.parameter as keyof typeof form.data];
			if (paramValue !== undefined && paramValue !== null) {
				queryParams.set(selectedTask.parameter, String(paramValue));
			}
		} else if (selectedTask.id === 'custom-report-4') {
			// Validation ensures these exist if task 4 is selected
			queryParams.set('min_height', String(form.data.min_height));
			queryParams.set('max_height', String(form.data.max_height));
			queryParams.set('min_width', String(form.data.min_width));
			queryParams.set('max_width', String(form.data.max_width));
		}

		const queryString = queryParams.toString();
		if (queryString) {
			apiUrl += `?${queryString}`;
		}
		const response = await fetch(apiUrl);

		if (!response.ok) {
			let errorText = `API Error ${response.status}: ${response.statusText}`;
			const errorJson = await response.json();
			errorText = errorJson.error || errorText;
			throw new Error(errorText);
		}

		const data = await response.json();

		if (Array.isArray(data)) {
			results = data;
			if (data.length > 0) {
				headers = Object.keys(data[0]);
			}
		} else {
			console.warn('API response was not an array:', data);
			apiError = 'Received unexpected data format from API.';
		}
		return message(form, {
			results,
			headers,
			apiError,
			selectedTaskName: selectedTask.name
		});
	}
};
