/**
 * Example test file to verify Jest is set up correctly
 */

describe('Example Test Suite', () => {
  it('should pass a basic test', () => {
    expect(true).toBe(true)
  })

  it('should perform basic arithmetic', () => {
    expect(2 + 2).toBe(4)
  })

  it('should handle strings', () => {
    expect('PyQuest').toContain('Quest')
  })
})

describe('Array operations', () => {
  it('should filter arrays correctly', () => {
    const numbers = [1, 2, 3, 4, 5]
    const evens = numbers.filter(n => n % 2 === 0)
    expect(evens).toEqual([2, 4])
  })

  it('should map arrays correctly', () => {
    const numbers = [1, 2, 3]
    const doubled = numbers.map(n => n * 2)
    expect(doubled).toEqual([2, 4, 6])
  })
})
