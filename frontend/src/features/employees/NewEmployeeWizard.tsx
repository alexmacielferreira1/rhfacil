import { useState } from 'react'

import { CONTRACT_TYPE_LABELS, type ContractType, type Employee, type EmployeeInput } from './employees-api'

type FormState = {
  full_name: string
  email: string
  job_title: string
  department: string
  admission_date: string
  manager_id: string
  contract_type: ContractType | ''
  level: string
  cost_center: string
  salary_amount: string
}

const emptyForm: FormState = {
  full_name: '',
  email: '',
  job_title: '',
  department: '',
  admission_date: '',
  manager_id: '',
  contract_type: '',
  level: '',
  cost_center: '',
  salary_amount: '',
}

const steps = ['Dados pessoais', 'Dados profissionais', 'Revisão'] as const

export function NewEmployeeWizard({
  managers,
  onSubmit,
  isPending,
  isError,
  successMessage,
}: {
  managers: Employee[]
  onSubmit: (payload: EmployeeInput) => void
  isPending: boolean
  isError: boolean
  successMessage: string
}) {
  const [step, setStep] = useState(0)
  const [form, setForm] = useState<FormState>(emptyForm)

  function set<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  const step0Valid = form.full_name.trim().length >= 2 && !!form.email
  const step1Valid = form.job_title.trim().length >= 2 && form.department.trim().length >= 2 && !!form.admission_date

  function submit() {
    onSubmit({
      full_name: form.full_name,
      email: form.email,
      job_title: form.job_title,
      department: form.department,
      admission_date: form.admission_date,
      manager_id: form.manager_id || null,
      contract_type: form.contract_type || null,
      level: form.level || null,
      cost_center: form.cost_center || null,
      salary_amount: form.salary_amount || null,
    })
    setForm(emptyForm)
    setStep(0)
  }

  return (
    <div className="wizard">
      <ol className="wizard-steps">
        {steps.map((label, index) => (
          <li key={label} className={index === step ? 'active' : index < step ? 'done' : ''}>
            <span>{index + 1}</span> {label}
          </li>
        ))}
      </ol>

      {step === 0 && (
        <div className="form-card">
          <label>Nome completo<input value={form.full_name} onChange={(e) => set('full_name', e.target.value)} required minLength={2} /></label>
          <label>E-mail<input type="email" value={form.email} onChange={(e) => set('email', e.target.value)} required /></label>
          <div className="wizard-actions">
            <button type="button" disabled={!step0Valid} onClick={() => setStep(1)}>Próximo</button>
          </div>
        </div>
      )}

      {step === 1 && (
        <div className="form-card">
          <label>Cargo<input value={form.job_title} onChange={(e) => set('job_title', e.target.value)} required minLength={2} /></label>
          <label>Departamento<input value={form.department} onChange={(e) => set('department', e.target.value)} required minLength={2} /></label>
          <label>Data de admissão<input type="date" value={form.admission_date} onChange={(e) => set('admission_date', e.target.value)} required /></label>
          <label>
            Gestor direto
            <select value={form.manager_id} onChange={(e) => set('manager_id', e.target.value)}>
              <option value="">Sem gestor definido</option>
              {managers.map((m) => (
                <option key={m.id} value={m.id}>{m.full_name}</option>
              ))}
            </select>
          </label>
          <label>
            Tipo de contratação
            <select value={form.contract_type} onChange={(e) => set('contract_type', e.target.value as ContractType | '')}>
              <option value="">Não informado</option>
              {(Object.keys(CONTRACT_TYPE_LABELS) as ContractType[]).map((key) => (
                <option key={key} value={key}>{CONTRACT_TYPE_LABELS[key]}</option>
              ))}
            </select>
          </label>
          <label>Nível / grade<input value={form.level} onChange={(e) => set('level', e.target.value)} placeholder="Ex.: Pleno, Nível 2" /></label>
          <label>Centro de custo<input value={form.cost_center} onChange={(e) => set('cost_center', e.target.value)} placeholder="Ex.: TEC-001" /></label>
          <label>Salário fixo (R$)<input type="number" min="0" step="0.01" value={form.salary_amount} onChange={(e) => set('salary_amount', e.target.value)} /></label>
          <div className="wizard-actions">
            <button type="button" className="secondary" onClick={() => setStep(0)}>Voltar</button>
            <button type="button" disabled={!step1Valid} onClick={() => setStep(2)}>Próximo</button>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="form-card">
          <dl className="profile-fields">
            <div><dt>Nome</dt><dd>{form.full_name}</dd></div>
            <div><dt>E-mail</dt><dd>{form.email}</dd></div>
            <div><dt>Cargo</dt><dd>{form.job_title}</dd></div>
            <div><dt>Departamento</dt><dd>{form.department}</dd></div>
            <div><dt>Admissão</dt><dd>{form.admission_date}</dd></div>
            <div><dt>Gestor</dt><dd>{managers.find((m) => m.id === form.manager_id)?.full_name ?? 'Sem gestor'}</dd></div>
            <div><dt>Contratação</dt><dd>{form.contract_type ? CONTRACT_TYPE_LABELS[form.contract_type] : 'Não informado'}</dd></div>
            <div><dt>Nível</dt><dd>{form.level || 'Não informado'}</dd></div>
          </dl>
          <div className="wizard-actions">
            <button type="button" className="secondary" onClick={() => setStep(1)}>Voltar</button>
            <button type="button" disabled={isPending} onClick={submit}>{isPending ? 'Cadastrando…' : 'Confirmar cadastro'}</button>
          </div>
          {successMessage && <p className="success-message">{successMessage}</p>}
          {isError && <p role="alert">Não foi possível cadastrar o colaborador.</p>}
        </div>
      )}
    </div>
  )
}
