# 按显式 ANCIENT_CARDS 清单选择两类图窗;同一母版按内容类名落位。
mkdir -p "$DST/cards"
for path in "${!CARDS[@]}"; do
    cls="${CARDS[$path]}"
    size=750x570
    case " $ANCIENT_CARDS " in *" $cls "*) size=606x852 ;; esac
    convert "$SRC/$path" -resize "${size}^" -gravity center -extent "$size" "$DST/cards/$cls.png"
done
echo "卡图: ${#CARDS[@]} 张"
