unit Unit1;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, ExtCtrls, TeEngine, Series, TeeProcs, Chart;

type
  TForm1 = class(TForm)
    RadioGroup1: TRadioGroup;
    Edit1: TEdit;
    Label1: TLabel;
    Label2: TLabel;
    Edit2: TEdit;
    RadioGroup2: TRadioGroup;
    Label3: TLabel;
    Edit3: TEdit;
    Label4: TLabel;
    Edit4: TEdit;
    Button1: TButton;
    Label5: TLabel;
    Edit5: TEdit;
    Chart1: TChart;
    Series1: TBarSeries;
    procedure Button1Click(Sender: TObject);
    procedure FormCreate(Sender: TObject);
    procedure RadioGroup1Click(Sender: TObject);
    procedure RadioGroup2Click(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  Form1: TForm1;  tt:text;

implementation

{$R *.dfm}

procedure TForm1.Button1Click(Sender: TObject);
procedure StringRepl (var s:String; a,b : Char);
var i:integer; ss:string;
begin
    ss:='';
    if length(s)>0 then
    for i:=1 to length(s) do if s[i]<>'.' then ss:=ss+s[i] else ss:=ss+',';
    s:=ss;
end;
var Ztime,  {Текущее модельное время}
    TMod,   {Время моделирования}
    lamIst, {Интенсивность потока требований из источника}
    SkoIst, {Среднее квадратическое отклонение ср. потока из источника}
    lamCMO, {Интенсивность обслуживания требований}
    SkoCMO, {Среднее квадратическое отклонение от ср. обсл-я в СМО}
    TaCMO,  {Момент активизации СМО}
    TaIst   {Момент активизации Источника} : Extended;
    MpQ     {Момент постановки требовния в очередь} : array [1..1000] of extended;
    DS012   {для вычисления м.о. числа требований в СМО} : array [0..1000] of extended;
    DQ012   {для вычисления м.о. числа треб-й в оч-ди}   : array [0..1000] of extended;
    MpQS,   {Момент постановки требовния в очередь}
    MgQS    {Момент выбора требования из очереди}  : extended;
    NDQ     {Число требований в очереди} : integer;
    NDS     {Число требований в СМО} : integer;
    i       {Рабочая переменная} : longInt;
    nf,nf1,nf2  {номер ф.р. в модели} : integer;
    sum,s1,s2,a,b,c,sk1,sk2     {рабочая переменная} : extended;
    smsQ    {момент смены состояния} : extended;
    smsS    {момент смены состояния} : extended;
    izS     {индикатор занятости прибора: True-занят, false-свободен} : boolean;
    chot    {число обслуженных требований} : longInt;
    s:string;
begin
    {Устанавливаем начальное состояние модели}
    randomize;
    Ztime:=0;
    TMod:=1000000; {StrToFloat(Edit5.Text);}
    s:=Edit1.Text; StringRepl(s,'.',','); lamIst:=StrToFloat(s);
    s:=Edit2.Text; StringRepl(s,'.',','); SkoIst:=StrToFloat(s);
    s:=Edit3.Text; StringRepl(s,'.',','); lamCMO:=StrToFloat(s);
    s:=Edit4.Text; StringRepl(s,'.',','); SkoCMO:=StrToFloat(s);
    for i:=1 to 1000 do MpQ[i]:=0;  MpQS:=0; MgQS:=0;
    for i:=0 to 1000 do begin DS012[i]:=0; DQ012[i]:=0; end;
    izS:=false;
    NDQ:=0; NDS:=0;
    TaCMO:=TMod+1e+5;
    TaIst:=Ztime;
    smsQ:=Ztime; smsS:=Ztime;
    chot:=0;
    nf1:=RadioGroup1.ItemIndex; nf2:=RadioGroup2.ItemIndex;
    if ((nf1 =0) and (nf2 =0) and (lamIst>=lamCMO)) or
       ((nf1 =0) and (nf2<>0) and (lamIst>=1/lamCMO)) or
       ((nf1<>0) and (nf2 =0) and (1/lamIst>=lamCMO)) or
       ((nf1<>0) and (nf2<>0) and (lamIst<=lamCMO)) then
       begin
          ShowMessage('Интенсивность потока должна быть меньше инт-ти обслуживания');
          exit
       end;
    AssignFile(tt,'MOS.txt'); rewrite(tt);
    while Ztime<TMod do
    begin
       if TaIst=Ztime then {генерируется требование}
          begin
             DS012[NDS]:=DS012[NDS]+ztime-smsS;
             DQ012[NDQ]:=DQ012[NDQ]+ztime-smsQ;
             smsQ:=Ztime; smsS:=Ztime;
             NDQ:=NDQ+1; NDS:=NDS+1;
             MpQ[NDQ]:=Ztime;
             nf:=RadioGroup1.ItemIndex;
             case nf of
             0: TaIst:=Ztime-ln(random)/lamIst;
             1: begin
                   sum:=0;
                   for i:=1 to 12 do sum:=sum+random;
                   sum:=lamIst+SkoIst*(sum-6); if sum<0 then sum:=0.001;
                   TaIst:=Ztime+sum;
                end;
             2: TaIst:=Ztime+lamIst;
             end;
          end
                      else
       if (NDQ>0) and not izS then {начинается обслуживание требования}
          begin
             izS:=True;
             nf:=RadioGroup2.ItemIndex;
             case nf of
             0: TaCMO:=Ztime-ln(random)/lamCMO;
             1: begin
                   sum:=0;
                   for i:=1 to 12 do sum:=sum+random;
                   sum:=lamCMO+SkoCMO*(sum-6); if sum<0 then sum:=0.001;
                   TaCMO:=Ztime+sum;
                end;
             2: TaCMO:=Ztime+lamCMO;
             end;
             MpQS:=MpQ[1];
             MgQS:=Ztime;
             for i:=1 to NDQ-1 do MpQ[i]:=MpQ[i+1]; MpQ[NDQ]:=0;
             DQ012[NDQ]:=DQ012[NDQ]+ztime-smsQ; smsQ:=Ztime;
             NDQ:=NDQ-1;
          end
                              else
       if izS and (TaCMO=Ztime) then  {завершается обслуживание требования}
          begin
             izS:=false;
             chot:=chot+1;
             TaCMO:=TMod+1e+5;
             writeln(tt,MpQS,' ',MgQS,' ',Ztime);
             DS012[NDS]:=DS012[NDS]+ztime-smsS; smsS:=Ztime;
             NDS:=NDS-1;
          end
       else if TaCMO<TaIst then Ztime:=TaCMO else Ztime:=TaIst; {передвигаем время}
    end;
    CloseFile(tt);
    AssignFile(tt,'MOS.txt'); reset(tt);
    s1:=0; s2:=0;
    for i:=1 to chot do begin read(tt,a,b,c); s1:=s1+c-a; s2:=s2+b-a; end;
    s1:=s1/chot; s2:=s2/chot;
    CloseFile(tt);
    AssignFile(tt,'MOS.txt'); reset(tt);
    sk1:=0; sk2:=0;
    for i:=1 to chot do
       begin
          read(tt,a,b,c);
          sk1:=sk1+(s1-c+a)*(s1-c+a);
          sk2:=sk2+(s2-b+a)*(s2-b+a);
       end;
    sk1:=sqrt(sk1/(chot-1)); sk2:=sqrt(sk2/(chot-1));
    CloseFile(tt);
    DeleteFile('MOS.txt');
    AssignFile(tt,'res.txt'); rewrite(tt);
    writeln(tt,'м.о. длит. пребывания треб-й в СМО ',s1:8:4,'    с.к.о. =',sk1:8:4);
    writeln(tt,'м.о. длит. пребывания треб-й в очереди ',s2:8:4,'    с.к.о. =',sk2:8:4);
    a:=0;
    for i:=1 to 1000 do a:=a+i*DS012[i]/Tmod;
    b:=0;
    for i:=1 to 1000 do b:=b+i*DQ012[i]/Tmod;
    Chart1.Series[0].Clear;
    for i:=0 to 12 {20} do Chart1.SeriesList[0].AddXY(i,DS012[i]/Tmod,'',clBlue {Red});
    writeln(tt,'м.о. числа треб-й в СМО ',a:8:4);
    writeln(tt,'м.о. числа треб-й в очереди =',b:8:4);
    CloseFile(tt);
    {ShowMessage('++');}
end;

procedure TForm1.FormCreate(Sender: TObject);
begin
   label2.Visible:=False; Edit2.Visible:=False;
   label4.Visible:=False; Edit4.Visible:=False;
end;

procedure TForm1.RadioGroup1Click(Sender: TObject);
begin
   if RadioGroup1.ItemIndex=0 then
   begin
      label1.Caption:='Инт-ть потока зад-й';
      label2.Visible:=False; Edit2.Visible:=False;
   end;
   if RadioGroup1.ItemIndex=1 then
   begin
      label1.Caption:='Длит.м/у заданиями';
      label2.Visible:=True; Edit2.Visible:=True;
   end;
   if RadioGroup1.ItemIndex=2 then
   begin
      label1.Caption:='Длит.м/у заданиями';
      label2.Visible:=False; Edit2.Visible:=False;
   end;
end;

procedure TForm1.RadioGroup2Click(Sender: TObject);
begin
   if RadioGroup2.ItemIndex=0 then
   begin
      label3.Caption:='Инт-ть обслуж-я';
      label4.Visible:=False; Edit4.Visible:=False;
   end;
   if RadioGroup2.ItemIndex=1 then
   begin
      label3.Caption:='Длит. обслуж-я';
      label4.Visible:=True; Edit4.Visible:=True;
   end;
   if RadioGroup2.ItemIndex=2 then
   begin
      label3.Caption:='Длит. обслуж-я';
      label4.Visible:=False; Edit4.Visible:=False;
   end;
end;

end.