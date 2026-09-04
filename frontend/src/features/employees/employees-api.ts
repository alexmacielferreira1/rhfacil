import { apiGet, apiSend, apiUpload } from '../../lib/api-client'

export type EmployeeStatus = 'active' | 'inactive' | 'terminated'
export type ContractType = 'clt' | 'pj' | 'estagio' | 'temporario' | 'outro'

export const CONTRACT_TYPE_LABELS: Record<ContractType, string> = {
  clt: 'CLT',
  pj: 'PJ',
  estagio: 'Estágio',
  temporario: 'Temporário',
  outro: 'Outro',
}

export type EmployeeInput = {
  full_name: string
  email: string
  job_title: string
  department: string
  admission_date: string
  manager_id?: string | null
  contract_type?: ContractType | null
  level?: string | null
  cost_center?: string | null
  salary_amount?: string | null
}

export type Employee = {
  id: string
  full_name: string
  email: string
  job_title: string
  department: string
  status: EmployeeStatus
  admission_date: string
  termination_date: string | null
  manager_id: string | null
  manager_name: string | null
  contract_type: ContractType | null
  level: string | null
  cost_center: string | null
  salary_amount: string | null
  created_at: string
  updated_at: string
}

export type ImportRowResult = {
  row_number: number
  email: string
  outcome: 'created' | 'updated' | 'error'
  detail: string | null
}

export type ImportSummary = {
  created: number
  updated: number
  errors: number
  rows: ImportRowResult[]
}

export const EMPLOYEES_EXPORT_URL = '/api/v1/people/employees/export.csv'

export function listEmployees() {
  return apiGet<Employee[]>('/api/v1/people/employees')
}

export function createEmployee(payload: EmployeeInput) {
  return apiSend<Employee>('/api/v1/people/employees', 'POST', payload)
}

export function changeEmployeeStatus(employeeId: string, status: EmployeeStatus) {
  return apiSend<Employee>(`/api/v1/people/employees/${employeeId}/status`, 'POST', { status })
}

export function importEmployeesCsv(file: File) {
  return apiUpload<ImportSummary>('/api/v1/people/employees/import', file)
}
