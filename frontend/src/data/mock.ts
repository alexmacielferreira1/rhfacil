export type PageKey = 'inicio' | 'mapa' | 'abrigos' | 'plano' | 'notificacoes' | 'clima' | 'relatorios' | 'perfil' | 'configuracoes'

export const alerts = [
  { level: 'Alerta', title: 'Chuva forte', text: 'Chuva forte pode causar alagamentos nas próximas horas.', color: 'red', time: '09:41', place: 'Menino Deus · Porto Alegre' },
  { level: 'Atenção', title: 'Nível do Guaíba subindo', text: 'A estação Usina do Gasômetro registrou 1,84 m.', color: 'orange', time: '08:15', place: 'Porto Alegre' },
  { level: 'Normal', title: 'Abrigo com vagas confirmado', text: 'Abrigo São João tem vagas disponíveis.', color: 'green', time: '07:02', place: 'São João · Porto Alegre' },
]

export const shelters = [
  { name: 'Ginásio Tesourinha', distance: '1,2 km', time: '4 min', status: 'Aberto · vagas disponíveis', vacancies: '120 vagas', accessibility: true, pets: true },
  { name: 'E.M.E.F. José Loureiro', distance: '1,6 km', time: '6 min', status: 'Aberto · vagas disponíveis', vacancies: '85 vagas', accessibility: true, pets: true },
  { name: 'Centro Comunitário Azenha', distance: '2,3 km', time: '9 min', status: 'Aberto · lotação média', vacancies: '20 vagas', accessibility: true, pets: true },
]

export const cities = ['Porto Alegre', 'Canoas', 'São Leopoldo', 'Novo Hamburgo', 'Guaíba']
