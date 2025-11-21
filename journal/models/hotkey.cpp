/* Short PortionPct */
ExecHotkey("BestRoute");

$Side = "SHORT";
if ($config.risk_type == "FIXED") {
    $risk = $config.risk;
} else {
    $risk = $config.risk_pct * $config.account_obj.Equity;
}

if ($risk > 0) { 
    ExecHotkey("GetCurrentTicker");

    if (IsObj($config.symbols.Get($config.execution_montage_obj.SYMBOL))) {
        $Portion = $risk * $PortionPct;

        $StopPrice = $config.symbols.Get($config.execution_montage_obj.SYMBOL).data;

        /* Choose entry price for intended side */
        if ($Side == "SHORT") {
            if ($config.order_type == "MARKET") {
                $Price = $config.symbols.Get($config.execution_montage_obj.SYMBOL).Bid - $config.order_type_offsets.Get($config.order_type);
            } else {
                $Price = $config.symbols.Get($config.execution_montage_obj.SYMBOL).Ask + $config.order_type_offsets.Get($config.order_type); /* Limit Long */
            }

            $Delta = $StopPrice - $Price;
        } else {
            if ($config.order_type == "MARKET") {
                $Price = $config.symbols.Get($config.execution_montage_obj.SYMBOL).Ask + $config.order_type_offsets.Get($config.order_type);
            } else {
                $Price = $config.symbols.Get($config.execution_montage_obj.SYMBOL).Bid - $config.order_type_offsets.Get($config.order_type); /* Limit Long */
            }

            $Delta = $Price - $StopPrice;
        }

        if ($Delta <= 0) { 
            MsgBox("Stop invalid, it is at or above. Check stop position at "+ $StopPrice);
        } else {
            $Shares = Round($Portion / $Delta, 0);
            if ($Shares < 1) { 
                MsgBox("Not enough shares, risk would be too high if you add one share.");
            } else {
                ExecHotkey("ATR");
                MsgBox("Atr is: "+$atr); 
                if($Delta <= $atr) {
                    if (Input("SL is " + $StopPrice + " while entry price is " + $Price + ". Be careful, they are very close! Type 'yes' to continue."); == "yes") {
                    ExecHotkey("OrderCreation");
                    }
                } else {
                    ExecHotkey("OrderCreation");
                }

                if ($config.verbose) { MsgBox($config.order_type + " " + $Side + " " + $Shares + " @ " + $Price + " (" + $PortionPct*100 + "%)"); }
            }
        }
        
    } else {
        MsgBox("Set SL for the symbol first");
    }
} else {
   MsgBox("Set RiskPct first");
}
DelVar(Side, risk, PortionPct, Portion, StopPrice, Price, Delta, Shares);










/* Sell PortionPct */
ExecHotkey("BestRoute");
ExecHotkey("GetCurrentTicker");

if (IsObj($config.symbols.Get($config.execution_montage_obj.SYMBOL))) {
    $Pos = $config.account_obj.getposition($config.execution_montage_obj.SYMBOL);

    $Side = "";
    if ($Pos.Share >= 0) { 
        $Side = "SELL";
        
        $Shares = Round($Pos.Share * $PortionPct, 0);
        if ($Shares < 1) { $Shares = 1; }
        else if ($Shares > $Pos.Share) { $Shares = $Pos.Share; }

        if ($config.order_type == "MARKET") {
            $Price = $config.symbols.Get($config.execution_montage_obj.SYMBOL).Bid - $config.order_type_offsets.Get($config.order_type);
        } else {
            $Price = $config.symbols.Get($config.execution_montage_obj.SYMBOL).Ask + $config.order_type_offsets.Get($config.order_type); /* Limit Long */
        }

    } else if ($Pos.Share <= 0) { 
        $Side = "BUY";

        $Shares = Round(-1 * $Pos.Share * $PortionPct, 0);
        if ($Shares < 1) { $Shares = 1; }
        else if ($Shares > -1*$Pos.Share) { $Shares = -1*$Pos.Share; }
        
        if ($config.order_type == "MARKET") {
            $Price = $config.symbols.Get($config.execution_montage_obj.SYMBOL).Ask + $config.order_type_offsets.Get($config.order_type);
        } else {
            $Price = $config.symbols.Get($config.execution_montage_obj.SYMBOL).Bid - $config.order_type_offsets.Get($config.order_type); /* Limit Long */
        }
    } 

    if ($Side != "") {
        ExecHotkey("OrderCreation");

        DelVar(Side, PortionPct, Price, Shares);
    }

} else {
    MsgBox("Set SL for the symbol first");
}
