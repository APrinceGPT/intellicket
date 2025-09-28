// Icon mapping for FontAwesome classes to emoji strings
const iconClassMap: Record<string, string> = {
  'fas fa-exclamation-triangle': '⚠️',
  'fas fa-check-circle': '✅',
  'fas fa-cogs': '⚙️',
  'fas fa-shield-alt': '🛡️',
  'fas fa-star': '⭐',
  'fas fa-clock': '🕐',
  'fa-solid fa-triangle-exclamation': '⚠️',
  'fa-solid fa-check-circle': '✅',
  'fa-solid fa-chart-bar': '📊',
};

interface ParsedHtmlContent {
  icon?: string;
  text: string;
  priority: 'high' | 'medium' | 'low';
  type: 'performance' | 'security' | 'exclusion' | 'monitor' | 'success';
}

/**
 * Converts HTML strings with FontAwesome icons to structured React components
 */
export const parseHtmlRecommendation = (htmlString: string): ParsedHtmlContent => {
  // Check if this is a plain text recommendation
  if (!htmlString.includes('<') && !htmlString.includes('>')) {
    return {
      text: htmlString,
      priority: 'medium',
      type: 'monitor'
    };
  }

  // Extract icon information
  const iconMatch = htmlString.match(/<i\s+class="([^"]+)"[^>]*><\/i>/);
  let icon: string | undefined = undefined;
  let text = htmlString;

  if (iconMatch) {
    const iconClasses = iconMatch[1];
    
    // Map FontAwesome classes to emoji
    icon = iconClassMap[iconClasses] || iconClassMap[iconClasses.replace(/text-\w+/, '')] || '💡';
    
    // Remove the icon HTML from text
    text = text.replace(/<i\s+class="[^"]+"[^>]*><\/i>\s*/, '');
  }

  // Clean up any remaining HTML tags
  text = text
    .replace(/<strong>/g, '')
    .replace(/<\/strong>/g, '')
    .replace(/<br\s*\/?>/g, ' ')
    .replace(/<[^>]*>/g, '')
    .trim();

  // Determine priority based on keywords
  const priority = determinePriority(text);
  
  // Determine type based on content
  const type = determineType(text);

  return {
    icon,
    text,
    priority,
    type
  };
};

/**
 * Determines recommendation priority based on text content
 */
const determinePriority = (text: string): 'high' | 'medium' | 'low' => {
  const lowerText = text.toLowerCase();
  
  if (lowerText.includes('critical') || 
      lowerText.includes('immediate') || 
      lowerText.includes('urgent') || 
      lowerText.includes('high scan volume') ||
      lowerText.includes('security review required')) {
    return 'high';
  }
  
  if (lowerText.includes('important') || 
      lowerText.includes('should') || 
      lowerText.includes('recommended') ||
      lowerText.includes('focus on') ||
      lowerText.includes('priority')) {
    return 'medium';
  }
  
  return 'low';
};

/**
 * Determines recommendation type based on text content
 */
const determineType = (text: string): 'performance' | 'security' | 'exclusion' | 'monitor' | 'success' => {
  const lowerText = text.toLowerCase();
  
  if (lowerText.includes('optimal') || 
      lowerText.includes('no exclusions needed') ||
      lowerText.includes('functioning within normal')) {
    return 'success';
  }
  
  if (lowerText.includes('exclusion') || 
      lowerText.includes('exclude') ||
      lowerText.includes('priority exclusion candidates')) {
    return 'exclusion';
  }
  
  if (lowerText.includes('security') || 
      lowerText.includes('risk') ||
      lowerText.includes('security review')) {
    return 'security';
  }
  
  if (lowerText.includes('performance') || 
      lowerText.includes('optimization') ||
      lowerText.includes('scan volume') ||
      lowerText.includes('focus on')) {
    return 'performance';
  }
  
  return 'monitor';
};

/**
 * Converts a list of HTML recommendation strings to structured format
 */
export const parseHtmlRecommendations = (htmlRecommendations: string[]): ParsedHtmlContent[] => {
  return htmlRecommendations.map(parseHtmlRecommendation);
};

/**
 * Gets appropriate emoji/icon for recommendation type and priority
 */
export const getRecommendationEmoji = (type: string, priority: string): string => {
  if (type === 'success') return '✅';
  if (type === 'security') return '🛡️';
  if (type === 'exclusion') return '🎯';
  if (type === 'performance') {
    return priority === 'high' ? '🚨' : priority === 'medium' ? '⚡' : '📊';
  }
  return '💡';
};

/**
 * Gets appropriate color class for recommendation type and priority
 */
export const getRecommendationColorClass = (type: string, priority: string): string => {
  if (type === 'success') return 'text-green-400 bg-green-900/20 border-green-400/30';
  if (priority === 'high') return 'text-red-400 bg-red-900/20 border-red-400/30';
  if (priority === 'medium') return 'text-yellow-400 bg-yellow-900/20 border-yellow-400/30';
  return 'text-blue-400 bg-blue-900/20 border-blue-400/30';
};
