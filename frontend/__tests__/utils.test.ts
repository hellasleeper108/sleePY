/**
 * Tests for utility functions
 */

import { getDifficultyBadgeColor, formatXP } from '@/lib/utils'

describe('Utility Functions', () => {
  describe('getDifficultyBadgeColor', () => {
    it('should return correct color for beginner', () => {
      const color = getDifficultyBadgeColor('beginner')
      expect(color).toContain('green')
    })

    it('should return correct color for intermediate', () => {
      const color = getDifficultyBadgeColor('intermediate')
      expect(color).toContain('yellow')
    })

    it('should return correct color for advanced', () => {
      const color = getDifficultyBadgeColor('advanced')
      expect(color).toContain('orange')
    })

    it('should return correct color for expert', () => {
      const color = getDifficultyBadgeColor('expert')
      expect(color).toContain('red')
    })

    it('should default to beginner for unknown difficulty', () => {
      const color = getDifficultyBadgeColor('unknown')
      expect(color).toContain('green')
    })
  })

  describe('formatXP', () => {
    it('should format numbers with commas', () => {
      expect(formatXP(50)).toBe('50')
      expect(formatXP(999)).toBe('999')
      expect(formatXP(1000)).toBe('1,000')
      expect(formatXP(12345)).toBe('12,345')
      expect(formatXP(1000000)).toBe('1,000,000')
    })

    it('should handle zero', () => {
      expect(formatXP(0)).toBe('0')
    })

    it('should handle negative numbers', () => {
      expect(formatXP(-100)).toBe('-100')
    })
  })
})
