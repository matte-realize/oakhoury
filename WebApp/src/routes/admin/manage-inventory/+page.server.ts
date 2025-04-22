import { API_ROUTE } from '$lib/constants';
import { error, fail, redirect } from '@sveltejs/kit';
import { message, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { z } from 'zod';
import type { Actions, PageServerLoad } from './$types';

const treeInventorySchema = z.object({
	id: z.number().int().positive(),
	common_name: z.string(),
	scientific_name: z.string(),
	inventory: z.coerce.number().int().min(0, 'Inventory cannot be negative.')
});

const inventoryFormSchema = z.object({
	trees: z.array(treeInventorySchema)
});

interface ApiTree {
	id: number;
	common_name: string;
	scientific_name: string;
	inventory: number;
}

export const load: PageServerLoad = async ({ locals, fetch }) => {
	if (!locals.user) {
		throw redirect(302, '/login?redirectTo=/admin/manage-inventory');
	}
	const isMemberApiUrl = `${API_ROUTE}/is_organization_member?user_id=${encodeURIComponent(locals.user.id)}`;
	try {
		const isMemberResponse = await fetch(isMemberApiUrl);
		if (!isMemberResponse.ok) throw new Error('Failed permission check');
		const { is_organization_member } = await isMemberResponse.json();
		if (!is_organization_member) {
			throw error(403, 'Forbidden: You do not have permission to access this page.');
		}
	} catch (err) {
		console.error('Auth check failed:', err);
		throw error(500, 'Failed to verify permissions.');
	}

	// Fetch current tree inventory
	let currentTrees: ApiTree[] = [];
	const treesRes = await fetch(`${API_ROUTE}/trees`);
	if (!treesRes.ok) {
		throw error(treesRes.status, `Failed to load tree data: ${await treesRes.text()}`);
	}
	currentTrees = await treesRes.json();

	const form = await superValidate({ trees: currentTrees }, zod(inventoryFormSchema));

	return { form, trees: currentTrees };
};

export const actions: Actions = {
	default: async ({ request, fetch, locals }) => {
		if (!locals.user) throw error(401, 'Not authenticated');

		const form = await superValidate(request, zod(inventoryFormSchema));

		if (!form.valid) {
			console.error('Form validation failed:', form.errors);
			return fail(400, { form });
		}

		const updates = form.data.trees;
		let successCount = 0;
		let errorCount = 0;
		const errors: string[] = [];

		for (const tree of updates) {
			const response = await fetch(`${API_ROUTE}/update-tree-inventory`, {
				method: 'PATCH',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					tree_id: tree.id,
					inventory: tree.inventory
				})
			});

			if (!response.ok) {
				const errorBody = await response.text();
				console.error(
					`API Error updating inventory for tree ${tree.id} (${tree.common_name}): ${response.status} ${errorBody}`
				);
				errors.push(`Failed to update ${tree.common_name}: ${errorBody || response.statusText}`);
				errorCount++;
			} else {
				successCount++;
			}
		}

		if (errorCount > 0) {
			const errorMessage = `Inventory update completed with ${errorCount} error(s). ${successCount} updated successfully. Errors: ${errors.join('; ')}`;
			return message(form, errorMessage, { status: 500 });
		}

		return message(form, 'Inventory updated successfully!');
	}
};
