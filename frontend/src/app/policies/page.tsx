import React from "react";
import { ShieldCheck, Save, FileText } from "lucide-react";

export default function PoliciesPage() {
  const policyCode = `package veridex.authz

import rego.v1

default allow = false

# System Admins can do anything
allow if {
    "system_admin" in input.user.roles
}

# Workspace Admins can access their own workspace resources
allow if {
    "workspace_admin" in input.user.roles
    tenant_match
}

# Standard users can only read their own workspace resources
allow if {
    "standard_user" in input.user.roles
    input.action == "get"
    tenant_match
}

# Tenant matching logic
tenant_match if {
    input.user.organization_id == input.resource.organization_id
}
`;

  return (
    <div className="flex flex-col h-full bg-[#0B0E12] font-body text-[#F6F4EF]">
      <header className="px-6 py-4 flex items-center justify-between border-b border-white/5 backdrop-blur-sm bg-[#0B0E12]/80 sticky top-0 z-10 shrink-0">
        <h1 className="text-sm font-display font-bold text-[#F6F4EF] flex items-center gap-2">
          <ShieldCheck size={16} className="text-[#4C9FE8]" />
          Governance & Policies
        </h1>
        <button className="flex items-center gap-2 px-4 py-1.5 bg-[#4C9FE8]/10 text-[#4C9FE8] border border-[#4C9FE8]/20 hover:bg-[#4C9FE8]/20 transition-colors rounded-full text-xs font-mono">
          <Save size={14} />
          Save Policy
        </button>
      </header>

      <main className="flex-1 p-8 max-w-5xl mx-auto w-full flex flex-col">
        <div className="mb-6">
          <h2 className="text-xl font-display font-bold text-white mb-2">Open Policy Agent (OPA)</h2>
          <p className="text-sm text-white/40 font-mono">Declarative access control policies evaluated at runtime.</p>
        </div>

        <div className="flex-1 rounded-xl border border-white/5 bg-white/[0.02] overflow-hidden flex flex-col shadow-2xl shadow-black/50">
          <div className="px-4 py-3 border-b border-white/5 bg-white/[0.01] flex items-center gap-2">
            <FileText size={14} className="text-white/40" />
            <span className="font-mono text-xs text-white/60">authz.rego</span>
            <div className="ml-auto flex items-center gap-2">
               <span className="flex h-2 w-2 rounded-full bg-[#2FAE86]"></span>
               <span className="font-mono text-[10px] text-white/40">Active</span>
            </div>
          </div>
          <div className="flex-1 p-0 relative">
            {/* Real app would use Monaco Editor here */}
            <textarea 
              className="w-full h-full bg-[#0B0E12] text-[#F6F4EF]/80 font-mono text-sm p-6 resize-none focus:outline-none focus:ring-1 focus:ring-[#4C9FE8]/50"
              defaultValue={policyCode}
              spellCheck={false}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
