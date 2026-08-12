"use client";

import React, { useState, useEffect } from "react";
import { ShieldCheck, Search, CheckCircle2, XCircle, ShieldAlert, Plus, Save, Trash2, Edit } from "lucide-react";
import { GovernanceService, OpenAPI } from "@/client";
import { toast } from "sonner";
import { useAuth } from "@/context/AuthContext";

export default function PoliciesPage() {
  const { user } = useAuth();
  const [roles, setRoles] = useState<any[]>([]);
  const [policies, setPolicies] = useState<any[]>([]);
  
  const [simulation, setSimulation] = useState({ resource: "project", action: "write", userId: "" });
  const [simResult, setSimResult] = useState<any | null>(null);

  const [isRoleModalOpen, setIsRoleModalOpen] = useState(false);
  const [newRole, setNewRole] = useState({ name: "", description: "" });

  const [selectedRole, setSelectedRole] = useState<any | null>(null);
  const [editingPermissions, setEditingPermissions] = useState<{name: string, resource: string, action: string}[]>([]);

  const fetchGovernanceData = async () => {
    try {
      const fetchedRoles = await GovernanceService.getRolesApiV1GovernanceRolesGet();
      setRoles(fetchedRoles);
      const fetchedPolicies = await GovernanceService.getPoliciesApiV1GovernancePoliciesGet();
      setPolicies(fetchedPolicies);
    } catch (e) {
      console.error(e);
      toast.error("Failed to load governance data");
    }
  };

  useEffect(() => {
    if (user) {
      fetchGovernanceData();
    }
  }, [user]);

  const handleSimulate = async () => {
    try {
      const data = await GovernanceService.simulatePolicyApiV1GovernanceSimulatePost(
        simulation.resource,
        simulation.action,
        simulation.userId
      );
      setSimResult(data);
    } catch (e) {
      console.error(e);
      setSimResult({ allow: false, reason: "Error contacting server" });
    }
  };

  const handleCreateRole = async () => {
    if (!newRole.name) return;
    try {
      await GovernanceService.createRoleApiV1GovernanceRolesPost({
        name: newRole.name,
        description: newRole.description
      });
      toast.success("Role created successfully");
      setIsRoleModalOpen(false);
      setNewRole({ name: "", description: "" });
      fetchGovernanceData();
    } catch (e) {
      toast.error("Failed to create role");
    }
  };

  const handleOpenPermissions = (roleId: string) => {
    const policy = policies.find(p => p.role_id === roleId);
    setSelectedRole(roles.find(r => r.id === roleId));
    setEditingPermissions(policy ? [...policy.permissions] : []);
  };

  const handleAddPermission = () => {
    setEditingPermissions([...editingPermissions, { name: "New Permission", resource: "project", action: "read" }]);
  };

  const handleRemovePermission = (index: number) => {
    setEditingPermissions(editingPermissions.filter((_, i) => i !== index));
  };

  const handlePermissionChange = (index: number, field: string, value: string) => {
    const newPerms = [...editingPermissions];
    newPerms[index] = { ...newPerms[index], [field]: value };
    setEditingPermissions(newPerms);
  };

  const handleSavePermissions = async () => {
    if (!selectedRole) return;
    try {
      await GovernanceService.updateRolePermissionsApiV1GovernanceRolesRoleIdPermissionsPut(
        selectedRole.id,
        editingPermissions
      );
      toast.success("Permissions updated successfully");
      setSelectedRole(null);
      fetchGovernanceData();
    } catch (e) {
      toast.error("Failed to update permissions");
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#0B0E12] font-body text-[#F6F4EF] overflow-y-auto">
      <header className="px-6 py-4 flex items-center justify-between border-b border-white/5 backdrop-blur-sm bg-[#0B0E12]/80 sticky top-0 z-10 shrink-0">
        <h1 className="text-sm font-display font-bold text-[#F6F4EF] flex items-center gap-2">
          <ShieldCheck size={16} className="text-[#4C9FE8]" />
          Governance & Access Control
        </h1>
        <button 
          onClick={() => setIsRoleModalOpen(true)}
          className="flex items-center gap-2 px-3 py-1.5 bg-[#4C9FE8]/10 text-[#4C9FE8] hover:bg-[#4C9FE8]/20 border border-[#4C9FE8]/20 rounded-md text-xs font-medium transition-colors"
        >
          <Plus size={14} />
          Create Role
        </button>
      </header>

      <main className="flex-1 p-8 max-w-6xl mx-auto w-full flex flex-col gap-8">
        
        {/* Role Matrix */}
        <section className="rounded-xl border border-white/5 bg-white/[0.02] overflow-hidden shadow-2xl shadow-black/50 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-display font-bold text-white">Role Matrix</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-white/5 text-white/50">
                  <th className="pb-3 font-medium">Role</th>
                  <th className="pb-3 font-medium">Description</th>
                  <th className="pb-3 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {roles.map((role: any) => (
                  <tr key={role.id} className="border-b border-white/5 last:border-0 hover:bg-white/[0.01] transition-colors group">
                    <td className="py-4 text-[#4C9FE8] font-medium">{role.name}</td>
                    <td className="py-4 text-white/70">{role.description}</td>
                    <td className="py-4 text-right">
                      <button 
                        onClick={() => handleOpenPermissions(role.id)}
                        className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-white/10 rounded-md text-white/60 hover:text-white transition-all"
                      >
                        <Edit size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
                {roles.length === 0 && (
                  <tr>
                    <td colSpan={3} className="py-4 text-white/40 text-center">No roles found.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        {/* Simulator */}
        <section className="rounded-xl border border-white/5 bg-white/[0.02] overflow-hidden shadow-2xl shadow-black/50 p-6 flex flex-col gap-4">
          <h2 className="text-lg font-display font-bold text-white flex items-center gap-2">
            <Search size={18} className="text-[#4C9FE8]" />
            Policy Simulator
          </h2>
          <p className="text-sm text-white/40">Test access control rules dynamically against the policy engine.</p>
          
          <div className="flex gap-4 items-end mt-2">
            <label className="flex flex-col gap-1.5 flex-1">
              <span className="text-xs text-white/60 uppercase tracking-wider font-semibold">User ID</span>
              <input 
                type="text" 
                value={simulation.userId}
                onChange={e => setSimulation(s => ({...s, userId: e.target.value}))}
                className="w-full bg-[#0B0E12] border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-[#4C9FE8] transition-colors"
                placeholder="00000000-0000-0000-0000-000000000000"
              />
            </label>
            <label className="flex flex-col gap-1.5 flex-1">
              <span className="text-xs text-white/60 uppercase tracking-wider font-semibold">Resource</span>
              <input 
                type="text"
                value={simulation.resource}
                onChange={e => setSimulation(s => ({...s, resource: e.target.value}))}
                className="w-full bg-[#0B0E12] border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-[#4C9FE8] transition-colors"
                placeholder="e.g. project"
              />
            </label>
            <label className="flex flex-col gap-1.5 flex-1">
              <span className="text-xs text-white/60 uppercase tracking-wider font-semibold">Action</span>
              <select 
                value={simulation.action}
                onChange={e => setSimulation(s => ({...s, action: e.target.value}))}
                className="w-full bg-[#0B0E12] border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-[#4C9FE8] transition-colors"
              >
                <option value="read">Read (GET)</option>
                <option value="write">Write (POST/PUT)</option>
                <option value="delete">Delete (DELETE)</option>
                <option value="*">All Access (*)</option>
              </select>
            </label>
            <button 
              onClick={handleSimulate}
              disabled={!simulation.userId}
              className="px-6 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-lg font-medium text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed border border-white/10"
            >
              Simulate
            </button>
          </div>

          {simResult && (
            <div className={`mt-4 p-4 border rounded-lg flex items-start gap-3 ${simResult.allow ? "bg-[#2FAE86]/10 border-[#2FAE86]/20" : "bg-[#E64C4C]/10 border-[#E64C4C]/20"}`}>
              {simResult.allow ? (
                <CheckCircle2 className="text-[#2FAE86] shrink-0" />
              ) : (
                <XCircle className="text-[#E64C4C] shrink-0" />
              )}
              <div>
                <h4 className={`text-sm font-bold ${simResult.allow ? "text-[#2FAE86]" : "text-[#E64C4C]"}`}>
                  {simResult.allow ? "Access Granted" : "Access Denied"}
                </h4>
                <p className="text-sm mt-1 text-white/80">{simResult.reason}</p>
                {simResult.policy_id && (
                  <p className="text-xs mt-2 text-white/40 font-mono">Matched Rule: {simResult.policy_id}</p>
                )}
              </div>
            </div>
          )}
        </section>
      </main>

      {/* Role Creation Modal */}
      {isRoleModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-[#12161b] border border-white/10 rounded-xl w-full max-w-md shadow-2xl overflow-hidden flex flex-col">
            <div className="px-6 py-4 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
              <h3 className="font-display font-bold text-white">Create New Role</h3>
              <button onClick={() => setIsRoleModalOpen(false)} className="text-white/40 hover:text-white transition-colors">
                <XCircle size={18} />
              </button>
            </div>
            <div className="p-6 flex flex-col gap-4">
              <label className="flex flex-col gap-1.5">
                <span className="text-xs text-white/60 uppercase tracking-wider font-semibold">Role Name</span>
                <input 
                  autoFocus
                  type="text" 
                  value={newRole.name}
                  onChange={e => setNewRole(s => ({...s, name: e.target.value}))}
                  className="w-full bg-[#0B0E12] border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-[#4C9FE8] transition-colors"
                  placeholder="e.g. auditor"
                />
              </label>
              <label className="flex flex-col gap-1.5">
                <span className="text-xs text-white/60 uppercase tracking-wider font-semibold">Description</span>
                <input 
                  type="text" 
                  value={newRole.description}
                  onChange={e => setNewRole(s => ({...s, description: e.target.value}))}
                  className="w-full bg-[#0B0E12] border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-[#4C9FE8] transition-colors"
                  placeholder="e.g. Read-only access to all logs"
                />
              </label>
            </div>
            <div className="px-6 py-4 border-t border-white/5 bg-white/[0.02] flex justify-end gap-3">
              <button onClick={() => setIsRoleModalOpen(false)} className="px-4 py-2 text-sm text-white/60 hover:text-white transition-colors">Cancel</button>
              <button onClick={handleCreateRole} className="px-4 py-2 bg-[#4C9FE8] hover:bg-[#3b8fd9] text-white rounded-lg text-sm font-medium transition-colors">
                Create
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Permissions Modal */}
      {selectedRole && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-[#12161b] border border-white/10 rounded-xl w-full max-w-2xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh]">
            <div className="px-6 py-4 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
              <h3 className="font-display font-bold text-white flex items-center gap-2">
                <ShieldCheck size={18} className="text-[#4C9FE8]"/> 
                Edit Permissions: {selectedRole.name}
              </h3>
              <button onClick={() => setSelectedRole(null)} className="text-white/40 hover:text-white transition-colors">
                <XCircle size={18} />
              </button>
            </div>
            <div className="p-6 overflow-y-auto flex-1 flex flex-col gap-4">
              {editingPermissions.length === 0 ? (
                <div className="text-center py-8 text-white/40 text-sm border border-dashed border-white/10 rounded-lg">
                  No permissions assigned to this role yet.
                </div>
              ) : (
                <div className="flex flex-col gap-3">
                  {editingPermissions.map((perm, idx) => (
                    <div key={idx} className="flex gap-3 items-center bg-white/[0.02] border border-white/5 p-3 rounded-lg">
                      <input 
                        type="text" 
                        value={perm.name}
                        onChange={e => handlePermissionChange(idx, 'name', e.target.value)}
                        placeholder="Permission Name"
                        className="flex-1 bg-[#0B0E12] border border-white/10 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:border-[#4C9FE8]"
                      />
                      <input 
                        type="text" 
                        value={perm.resource}
                        onChange={e => handlePermissionChange(idx, 'resource', e.target.value)}
                        placeholder="Resource (e.g. project)"
                        className="flex-1 bg-[#0B0E12] border border-white/10 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:border-[#4C9FE8]"
                      />
                      <select 
                        value={perm.action}
                        onChange={e => handlePermissionChange(idx, 'action', e.target.value)}
                        className="w-32 bg-[#0B0E12] border border-white/10 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:border-[#4C9FE8]"
                      >
                        <option value="read">read</option>
                        <option value="write">write</option>
                        <option value="delete">delete</option>
                        <option value="*">*</option>
                      </select>
                      <button onClick={() => handleRemovePermission(idx)} className="text-red-400 hover:text-red-300 p-1.5">
                        <Trash2 size={16} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
              
              <button 
                onClick={handleAddPermission}
                className="w-full py-3 border border-dashed border-white/20 hover:border-[#4C9FE8]/50 hover:bg-[#4C9FE8]/5 text-white/60 hover:text-[#4C9FE8] rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2 mt-2"
              >
                <Plus size={16} />
                Add Permission
              </button>
            </div>
            <div className="px-6 py-4 border-t border-white/5 bg-white/[0.02] flex justify-end gap-3">
              <button onClick={() => setSelectedRole(null)} className="px-4 py-2 text-sm text-white/60 hover:text-white transition-colors">Cancel</button>
              <button onClick={handleSavePermissions} className="flex items-center gap-2 px-4 py-2 bg-[#2FAE86] hover:bg-[#289572] text-white rounded-lg text-sm font-medium transition-colors">
                <Save size={14} />
                Save Permissions
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
