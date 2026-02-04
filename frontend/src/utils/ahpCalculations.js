/* AHP (Analytic Hierarchy Process) Calculations */

const RANDOM_INDEX = {
  1: 0,
  2: 0,
  3: 0.58,
  4: 0.90,
  5: 1.12,
  6: 1.24,
  7: 1.32,
  8: 1.41,
  9: 1.45,
  10: 1.49,
}

export function buildComparisonMatrix(criteria, comparisons = {}) {
  const n = criteria.length
  const matrix = Array(n).fill(0).map(() => Array(n).fill(1))

  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      const key = `${criteria[i]}-${criteria[j]}`
      const reverseKey = `${criteria[j]}-${criteria[i]}`

      if (comparisons[key]) {
        matrix[i][j] = comparisons[key]
        matrix[j][i] = 1 / comparisons[key]
      } else if (comparisons[reverseKey]) {
        matrix[j][i] = comparisons[reverseKey]
        matrix[i][j] = 1 / comparisons[reverseKey]
      } else {
        matrix[i][j] = 1
        matrix[j][i] = 1
      }
    }
  }

  return matrix
}

export function calculateWeights(matrix) {
  const n = matrix.length
  const weights = []

  for (let i = 0; i < n; i++) {
    let product = 1
    for (let j = 0; j < n; j++) {
      product *= matrix[i][j]
    }
    weights[i] = Math.pow(product, 1 / n)
  }

  const sum = weights.reduce((acc, w) => acc + w, 0)
  return weights.map(w => w / sum)
}

function calculateLambdaMax(matrix, weights) {
  const n = matrix.length
  const weightedSum = Array(n).fill(0)

  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      weightedSum[i] += matrix[i][j] * weights[j]
    }
  }

  let lambdaMax = 0
  for (let i = 0; i < n; i++) {
    lambdaMax += weightedSum[i] / weights[i]
  }

  return lambdaMax / n
}

function calculateCI(lambdaMax, n) {
  return (lambdaMax - n) / (n - 1)
}

export function calculateConsistencyRatio(matrix, weights) {
  const n = matrix.length

  if (n < 3) return 0

  const lambdaMax = calculateLambdaMax(matrix, weights)
  const CI = calculateCI(lambdaMax, n)
  const RI = RANDOM_INDEX[n] || 1.49

  return CI / RI
}

export function isConsistent(cr) {
  return cr < 0.1
}

export function calculateAHPWeights(criteria, comparisons) {
  const matrix = buildComparisonMatrix(criteria, comparisons)
  const weightArray = calculateWeights(matrix)
  const cr = calculateConsistencyRatio(matrix, weightArray)

  const weights = {}
  criteria.forEach((criterion, index) => {
    weights[criterion] = weightArray[index]
  })

  return {
    weights,
    consistencyRatio: cr,
    isConsistent: isConsistent(cr),
  }
}

export function getSaatyInterpretation(value) {
  const interpretations = {
    1: 'Equal importance',
    2: 'Weak importance',
    3: 'Moderate importance',
    4: 'Moderate plus',
    5: 'Strong importance',
    6: 'Strong plus',
    7: 'Very strong importance',
    8: 'Very strong plus',
    9: 'Extreme importance',
  }
  return interpretations[value] || 'Equal importance'
}
