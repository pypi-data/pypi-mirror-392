# Feasibility Analysis: Porting Path of Building Calculations to Python

## Executive Summary

**Short Answer**: Technically possible, but extremely complex and time-consuming. Path of Building's calculation engine is a massive codebase with thousands of lines of Lua code handling complex game mechanics.

## Scale of the Task

### Path of Building Codebase Size

Based on the GitHub repository structure:
- **Main calculation engine**: Located in `src/` directory
- **Data files**: Game data, skill trees, item databases
- **Lua modules**: Hundreds of files handling different aspects
- **Lines of code**: Estimated 50,000+ lines of Lua code
- **Complexity**: Handles all Path of Exile mechanics, including edge cases

### What Needs to Be Ported

1. **Modifier System** (~10,000+ lines)
   - Parsing item modifiers
   - Applying "increased" vs "more" modifiers
   - Modifier stacking rules
   - Conditional modifiers

2. **Damage Calculations** (~15,000+ lines)
   - Base damage from skills/weapons
   - Damage conversion (physical → elemental, etc.)
   - Critical strike calculations
   - Damage over time (DoT) calculations
   - Penetration and resistance calculations

3. **Defensive Calculations** (~10,000+ lines)
   - Life/Mana/Energy Shield calculations
   - Armour and physical damage reduction
   - Evasion and evade chance
   - Block, dodge, spell suppression
   - Maximum hit taken calculations
   - Effective Health Pool (EHP)

4. **Skill System** (~8,000+ lines)
   - Skill gem parsing
   - Support gem interactions
   - Skill-specific calculations
   - Cooldown and cast time calculations

5. **Item System** (~5,000+ lines)
   - Item parsing and validation
   - Unique item effects
   - Crafted modifiers
   - Item set calculations

6. **Passive Tree** (~5,000+ lines)
   - Node parsing
   - Keystone effects
   - Notable passives
   - Jewel calculations

7. **Configuration System** (~2,000+ lines)
   - Enemy settings
   - Buff/debuff calculations
   - Conditional modifiers
   - Situational calculations

## Challenges

### 1. Game Mechanics Complexity

Path of Exile has extremely complex mechanics:
- Hundreds of unique items with special effects
- Thousands of passive tree nodes
- Complex modifier interactions
- Edge cases and special rules

### 2. Maintenance Burden

- Path of Exile updates frequently
- New mechanics are added regularly
- Bugs need to be fixed
- Calculations need to stay accurate

### 3. Data Dependencies

- Game data files (monsters, skills, items)
- Passive skill tree data
- Unique item databases
- All need to be kept up-to-date

### 4. Testing Requirements

- Need to verify calculations match PoB
- Need to test edge cases
- Need to handle all build types
- Need to ensure accuracy

## Approaches

### Approach 1: Full Port (Not Recommended)

**Pros:**
- Complete independence from Lua
- Full control over codebase
- Can optimize for Python

**Cons:**
- Months/years of development
- Constant maintenance required
- High risk of bugs
- May never catch up to PoB updates

**Estimated Time**: 6-12 months full-time for basic functionality, years for complete parity

### Approach 2: Hybrid Approach (Recommended)

**Use PoB for calculations, Python for display and analysis**

1. **Keep using PoB's XML export** (current approach)
2. **Add Python-based visualization** to match PoB's UI
3. **Add Python-based analysis tools** that PoB doesn't have

**Pros:**
- Leverages existing, accurate calculations
- Focus on visualization and analysis
- Much faster development
- Lower maintenance burden

**Cons:**
- Still depends on PoB
- Need PoB installed/running

**Estimated Time**: 1-3 months for visualization

### Approach 3: Partial Port (Selective)

**Port only specific calculation modules**

Start with simpler calculations:
1. Basic stat calculations (life, mana, ES)
2. Simple DPS calculations
3. Resistance calculations
4. Gradually add more complex features

**Pros:**
- Incremental development
- Can start with most-used features
- Learn as you go

**Cons:**
- Still very time-consuming
- May never reach full parity
- Need to maintain compatibility

**Estimated Time**: 2-4 months for basic stats, 6+ months for DPS

### Approach 4: Lua Bridge (Advanced)

**Run Lua code from Python**

Use a Lua-Python bridge to execute PoB's Lua code:
- `lupa` (LuaJIT in Python)
- `pylua` (Lua in Python)

**Pros:**
- Reuse existing PoB code
- No need to rewrite calculations
- Can add Python wrappers

**Cons:**
- Complex integration
- Performance overhead
- Still need to understand Lua code
- May have compatibility issues

**Estimated Time**: 1-2 months for integration

## Recommended Solution: Enhanced Visualization

Instead of porting calculations, focus on **visualization and presentation**:

### Phase 1: Text-Based Display (1-2 weeks)
- Format stats similar to PoB's display
- Group stats by category
- Show breakdowns (like PoB's detailed view)

### Phase 2: HTML/Web Display (2-4 weeks)
- Create web interface using Flask/FastAPI
- Display stats in collapsible sections (like PoB)
- Add color coding and formatting
- Interactive tooltips and explanations

### Phase 3: Advanced Features (1-2 months)
- Comparison tools (compare two builds)
- Optimization suggestions
- Build analysis and recommendations
- Export to various formats

### Benefits:
- ✅ Much faster development
- ✅ Leverages accurate PoB calculations
- ✅ Focus on user experience
- ✅ Lower maintenance burden
- ✅ Can add features PoB doesn't have

## Implementation Plan for Visualization

### Step 1: Create Display Module

```python
# pobapi/display.py
class StatsDisplay:
    """Display stats in PoB-like format."""

    def format_offensive_stats(self, stats: Stats) -> str:
        """Format offensive stats section."""
        pass

    def format_defensive_stats(self, stats: Stats) -> str:
        """Format defensive stats section."""
        pass

    def format_detailed_breakdown(self, stats: Stats) -> str:
        """Format detailed breakdown like PoB."""
        pass
```

### Step 2: Create Web Interface

```python
# pobapi/web_ui.py
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/build/<import_code>')
def show_build(import_code):
    build = from_import_code(import_code)
    return render_template('build_stats.html', build=build)
```

### Step 3: Create HTML Templates

Create templates that match PoB's UI:
- Collapsible sections
- Color-coded damage types
- Detailed breakdowns
- Interactive tooltips

## Conclusion

**Recommendation**: Focus on **visualization and presentation** rather than porting calculations.

**Why:**
1. Path of Building's calculation engine is extremely complex
2. Full port would take months/years
3. Current approach (extracting from XML) is accurate and reliable
4. Visualization can be done much faster
5. Can add features PoB doesn't have

**Next Steps:**
1. Create enhanced text-based display
2. Build web interface for visualization
3. Add comparison and analysis tools
4. Consider partial port only if specific needs arise

## References

- [Path of Building Repository](https://github.com/PathOfBuildingCommunity/PathOfBuilding)
- [Path of Building Documentation](https://pathofbuilding.community)
- Current API: Extracts calculated values from PoB's XML export
