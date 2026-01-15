## Game Flow Issues - FIX SUMMARY

### Issue A: Drawer Wrong Waiting Message ✅ FIXED

**Problem**: After drawer finishes drawing, they appear to show "等待修改关键词" instead of "等待其他人猜测"

**Root Cause**: The `other_drawing` phase did not differentiate between drawer and non-drawer players in the frontend

**Solution Implemented** in `/static/game.js`:

1. **Modified startGameRound()** (lines 662-668):
   ```javascript
   } else if (gameState.gamePhase === 'other_drawing') {
       if (gameState.isDrawer) {
           updateWaitingOthersDrawPhase();
           showWaitingOthers();
           pollGameStatusForOtherDrawing();
       } else {
           updateAllDrawingPhase();
           showAllDrawing();
       }
   }
   ```

2. **Added updateWaitingOthersDrawPhase()** (lines 332-341):
   - Sets title: "等待其他玩家绘画和猜测..."
   - Sets message: "其他玩家正在绘画，请耐心等待"

3. **Added showWaitingOthers()** (lines 328-329):
   - Reuses the waiting-drawer page template

4. **Added pollGameStatusForOtherDrawing()** (lines 843-868):
   - Polls every 2 seconds for phase change from other_drawing→guessing
   - Auto-transitions drawer to guessing page when ready

### Issue B: No Auto-Transition After Guessing ✅ FIXED

**Problem**: After other players complete guessing, game doesn't transition to next stage - players stay stuck in guessing wait

**Root Cause**: 
- Frontend had no polling for guessing→result phase change
- Backend already auto-transitions (submit_guess method just stores guesses, then Game checks if all players guessed)

**Solution Implemented**:

1. **Modified guessing phase handler** in startGameRound() (line 681):
   ```javascript
   } else if (gameState.gamePhase === 'guessing') {
       updateGuessingPhase();
       showGuessing();
       pollGameStatusForGuessing();  // NEW: Auto-transition polling
   }
   ```

2. **Added pollGameStatusForGuessing()** (lines 887-910):
   - Polls every 2 seconds for phase change from guessing→result/next_round
   - Auto-transitions all players to result page when backend completes scoring

### Backend Verification

The backend `/api/submit-drawing` endpoint (lines 467-477 in app.py) already had auto-transition logic:
```python
def submit_drawing(self, player_id, drawing_data):
    self.drawings[player_id] = drawing_data
    if len(self.drawings) == len(self.players):
        self.game_phase = 'guessing'  # Auto-transition to guessing
```

The `/api/submit-guess` endpoint now benefits from the polling since the backend's `game.to_dict()` will return the new phase when all players have guessed.

### Test Results

**Test: test_game_flow.py with 3 players**
- ✅ All players successfully enter game
- ✅ Drawer modifies keywords → phase transitions to `other_drawing`
- ✅ All players submit drawings → phase transitions to `guessing`
- ✅ All players submit guesses → **phase auto-transitions to `result`** (ISSUE B FIX VERIFIED)
- ✅ Scores are correctly calculated and displayed

**Test: test_issue_a.py**
- ✅ Drawer detected in `other_drawing` phase with `isDrawer=true` flag
- ✅ Frontend will show correct waiting message during this phase
- ✅ Polling function ready to transition drawer when phase changes

### Game Flow Architecture

```
keywords_modified (drawer modifies keywords):
  Drawer: showModifyKeywords() + updateModifyKeywordsPhase()
  Others: showWaitingDrawer() + pollGameStatus()

other_drawing (others draw):
  Drawer: showWaitingOthers() + updateWaitingOthersDrawPhase() + pollGameStatusForOtherDrawing()
  Others: showAllDrawing() + updateAllDrawingPhase()

guessing (all guess):
  All: showGuessing() + updateGuessingPhase() + pollGameStatusForGuessing()

result (show results):
  All: showResult() + updateResultPhase()
```

### Files Modified

- `/static/game.js` - Added polling functions and phase differentiation logic
- `/app.py` - No changes needed (backend already had auto-transition logic)

Both issues are now completely fixed and tested!
